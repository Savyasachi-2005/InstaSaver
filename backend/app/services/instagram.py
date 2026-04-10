import json
import re
import logging
from html import unescape
from typing import Any
from urllib.parse import urlparse

import yt_dlp
from curl_cffi import requests as cffi_requests

from app.core.errors import AppError
from app.schemas.download import MediaItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def _is_instagram_url(value: str) -> bool:
    return bool(re.match(r"^https?://(www\.)?instagram\.com/.+", value.strip(), re.IGNORECASE))


def _is_reel_url(url: str) -> bool:
    return any(part in url.lower() for part in ["/reel/", "/reels/"])


def _is_post_url(url: str) -> bool:
    return any(part in url.lower() for part in ["/p/", "/tv/"])


def _extract_shortcode(url: str) -> str | None:
    """Pull the shortcode from a /p/, /reel/, /reels/, or /tv/ URL."""
    match = re.search(r"/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None


def _is_direct_media_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    lower = url.lower()
    if any(part in lower for part in ["/p/", "/reel/", "/reels/", "/tv/", "/stories/"]):
        return False
    host = (urlparse(url).hostname or "").lower()
    return host.endswith("cdninstagram.com") or host.endswith("fbcdn.net")


# ---------------------------------------------------------------------------
# HTML / meta-tag parsing helpers
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Dest": "document",
}


def _meta_content(html_text: str, prop_names: list[str]) -> str | None:
    for tag_match in re.finditer(r"<meta[^>]+>", html_text, re.IGNORECASE):
        tag = tag_match.group(0)
        lower = tag.lower()
        if not any(f'property="{name}"' in lower or f"property='{name}'" in lower for name in prop_names):
            continue
        content_match = re.search(r"content=['\"]([^'\"]+)['\"]", tag, re.IGNORECASE)
        if content_match:
            return unescape(content_match.group(1).strip())
    return None


def _resolve_media_url(entry: dict[str, Any]) -> str | None:
    candidates: list[str] = []
    for key in ["url", "video_url", "display_url", "thumbnail"]:
        value = entry.get(key)
        if isinstance(value, str):
            candidates.append(value)

    formats = entry.get("formats")
    if isinstance(formats, list):
        sorted_formats = sorted(
            [item for item in formats if isinstance(item, dict)],
            key=lambda item: (item.get("height") or 0, item.get("tbr") or 0),
            reverse=True,
        )
        for item in sorted_formats:
            fmt_url = item.get("url")
            if isinstance(fmt_url, str):
                candidates.append(fmt_url)

    for value in candidates:
        if _is_direct_media_url(value):
            return value
    return None


# ---------------------------------------------------------------------------
# Strategy 1: yt-dlp (anonymous, no cookies)
# ---------------------------------------------------------------------------

def _extract_via_ytdlp(url: str) -> list[MediaItem]:
    """
    Primary strategy: yt-dlp with NO cookies/auth.
    Works for most public reels and posts.
    """
    options: dict[str, Any] = {
        "quiet": True,
        "skip_download": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_warnings": True,
        "extractor_retries": 2,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return []
    except Exception as exc:
        logger.debug("yt-dlp extraction failed: %s", exc)
        return []

    entries = info.get("entries") or [info]
    is_reel = _is_reel_url(url)

    items: list[MediaItem] = []
    for idx, entry in enumerate(entries):
        if not entry:
            continue

        if is_reel:
            video_url = entry.get("url") or entry.get("webpage_url")
            if not video_url:
                continue
            items.append(MediaItem(
                id=str(entry.get("id") or idx),
                media_type="video",
                media_url=video_url,
                thumbnail_url=entry.get("thumbnail"),
                title=entry.get("title") or "Instagram Reel",
            ))
        else:
            media_url = _resolve_media_url(entry)
            if not media_url:
                continue
            ext = str(entry.get("ext") or "").lower()
            vcodec = str(entry.get("vcodec") or "").lower()
            media_type = "video" if ext in {"mp4", "mov", "m4v", "webm"} or (vcodec and vcodec != "none") else "image"
            items.append(MediaItem(
                id=str(entry.get("id") or idx),
                media_type=media_type,
                media_url=media_url,
                thumbnail_url=entry.get("thumbnail"),
                title=entry.get("title") or "Instagram Post",
            ))

    return items


# ---------------------------------------------------------------------------
# Strategy 2: Instagram page scraping via curl_cffi
# ---------------------------------------------------------------------------

def _extract_via_scrape(url: str) -> list[MediaItem]:
    """
    Fetch the Instagram page directly using curl_cffi (impersonates Chrome TLS).
    Falls back to embed page. Looks for video/image URLs in HTML and JSON data.
    """
    shortcode = _extract_shortcode(url)
    if not shortcode:
        return []

    is_reel = _is_reel_url(url)

    # Try the main page first, then the embed page
    if is_reel:
        urls_to_try = [
            f"https://www.instagram.com/reel/{shortcode}/",
            f"https://www.instagram.com/reel/{shortcode}/embed/",
        ]
    else:
        urls_to_try = [
            f"https://www.instagram.com/p/{shortcode}/",
            f"https://www.instagram.com/p/{shortcode}/embed/",
        ]

    for page_url in urls_to_try:
        try:
            response = cffi_requests.get(
                page_url,
                headers=_HEADERS,
                impersonate="chrome",
                timeout=15,
                allow_redirects=True,
            )
            if response.status_code != 200:
                continue
            html = response.text
        except Exception as exc:
            logger.debug("Scrape fetch failed for %s: %s", page_url, exc)
            continue

        items: list[MediaItem] = []
        image_url = _meta_content(html, ["og:image:secure_url", "og:image"])
        title = _meta_content(html, ["og:title"]) or "Instagram Media"

        # Check OG video meta tags
        video_url = _meta_content(html, ["og:video:secure_url", "og:video"])
        if video_url:
            items.append(MediaItem(
                id=f"scrape-{shortcode}",
                media_type="video",
                media_url=video_url,
                thumbnail_url=image_url,
                title=title,
            ))
            return items

        # Search for video URL patterns in embedded scripts/JSON
        video_patterns = [
            r'"video_url"\s*:\s*"([^"]+)"',
            r'"contentUrl"\s*:\s*"([^"]+)"',
            r'<video[^>]+src="([^"]+)"',
            r'"video_url":"([^"]+)"',
        ]
        for pattern in video_patterns:
            match = re.search(pattern, html)
            if match:
                found_url = (
                    unescape(match.group(1))
                    .replace("\\u0026", "&")
                    .replace("\\/", "/")
                    .replace("\\u002F", "/")
                )
                if found_url.startswith("http"):
                    items.append(MediaItem(
                        id=f"scrape-{shortcode}",
                        media_type="video",
                        media_url=found_url,
                        thumbnail_url=image_url,
                        title=title,
                    ))
                    return items

        # For images: check if og:image is a real CDN URL
        if image_url and _is_direct_media_url(image_url):
            items.append(MediaItem(
                id=f"scrape-{shortcode}",
                media_type="image",
                media_url=image_url,
                thumbnail_url=None,
                title=title,
            ))
            return items

    return []


# ---------------------------------------------------------------------------
# Strategy 3: Proxy services (ddinstagram, etc.)
# ---------------------------------------------------------------------------

_PROXY_DOMAINS = [
    "ddinstagram.com",
    "d.ddinstagram.com",
]


def _extract_via_proxy(url: str) -> list[MediaItem]:
    """
    Rewrites the Instagram URL through a public proxy/embed service and
    extracts the media URL from the OG meta tags in the response.
    """
    cleaned = url.strip()

    for domain in _PROXY_DOMAINS:
        try:
            proxy_url = re.sub(
                r"^https?://(www\.)?instagram\.com",
                f"https://{domain}",
                cleaned,
                flags=re.IGNORECASE,
            )
            response = cffi_requests.get(
                proxy_url,
                headers={
                    "User-Agent": _HEADERS["User-Agent"],
                    "Accept-Language": "en-US,en;q=0.9",
                },
                impersonate="chrome",
                timeout=15,
                allow_redirects=True,
            )
            if response.status_code != 200:
                continue

            html = response.text
            media_url = _meta_content(html, ["og:video:secure_url", "og:video", "og:image:secure_url", "og:image"])
            if not media_url:
                continue

            media_type = "video" if "og:video" in html.lower() else "image"
            title = _meta_content(html, ["og:title"]) or "Instagram Media"

            return [
                MediaItem(
                    id="proxy-0",
                    media_type=media_type,
                    media_url=media_url,
                    thumbnail_url=None,
                    title=title,
                )
            ]
        except Exception as exc:
            logger.debug("Proxy %s failed: %s", domain, exc)
            continue

    return []


# ---------------------------------------------------------------------------
# Orchestrator: try each strategy in order
# ---------------------------------------------------------------------------

def _extract_media(url: str) -> list[MediaItem]:
    """
    Multi-strategy extraction pipeline.
    Tries each method in order and returns the first successful result.
    """
    strategies = [
        ("yt-dlp", _extract_via_ytdlp),
        ("scrape", _extract_via_scrape),
        ("proxy", _extract_via_proxy),
    ]

    for name, strategy in strategies:
        try:
            logger.info("Trying strategy: %s", name)
            items = strategy(url)
            if items:
                logger.info("Strategy '%s' succeeded with %d item(s)", name, len(items))
                return items
            logger.info("Strategy '%s' returned no items, trying next...", name)
        except Exception as exc:
            logger.warning("Strategy '%s' raised: %s", name, exc)

    # All strategies failed
    raise AppError(
        "Could not extract media from this URL. "
        "Please verify the link is correct and the content is publicly accessible.",
        404,
    )


# ---------------------------------------------------------------------------
# Public API (used by routers)
# ---------------------------------------------------------------------------

def extract_reel(url: str) -> list[MediaItem]:
    cleaned = url.strip()
    if not _is_instagram_url(cleaned) or not _is_reel_url(cleaned):
        raise AppError("Please provide a valid Instagram Reel URL.", 422)
    return _extract_media(cleaned)


def extract_post(url: str) -> list[MediaItem]:
    cleaned = url.strip()
    if not _is_instagram_url(cleaned) or not _is_post_url(cleaned):
        raise AppError("Please provide a valid Instagram Post URL.", 422)
    return _extract_media(cleaned)
