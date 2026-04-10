import re
import os
from typing import Any
from urllib.parse import urlparse

import yt_dlp

from app.core.config import get_settings
from app.core.errors import AppError
from app.schemas.download import MediaItem

def _is_instagram_url(value: str) -> bool:
    return bool(re.match(r"^https?://(www\.)?instagram\.com/.+", value.strip(), re.IGNORECASE))


def _is_reel_url(url: str) -> bool:
    return any(part in url.lower() for part in ["/reel/", "/reels/"])


def _is_post_url(url: str) -> bool:
    return any(part in url.lower() for part in ["/p/", "/tv/"])


def _is_direct_media_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False

    lower = url.lower()
    if any(part in lower for part in ["/p/", "/reel/", "/reels/", "/tv/", "/stories/"]):
        return False

    host = (urlparse(url).hostname or "").lower()
    return host.endswith("cdninstagram.com") or host.endswith("fbcdn.net")


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


def _ydl_options() -> dict[str, Any]:
    settings = get_settings()
    options: dict[str, Any] = {
        "quiet": True,
        "skip_download": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_warnings": True,
        "extractor_retries": 1,
    }

    if settings.instagram_cookies_file:
        options["cookiefile"] = settings.instagram_cookies_file
    elif settings.instagram_cookies_browser:
        # Browser cookie extraction is not available in Vercel serverless runtime.
        if not os.getenv("VERCEL"):
            browser = settings.instagram_cookies_browser.strip().lower()
            profile = (settings.instagram_cookies_browser_profile or "").strip()
            options["cookiesfrombrowser"] = (browser, profile) if profile else (browser,)

    return options


def _extract(url: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        with yt_dlp.YoutubeDL(_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise AppError("We could not extract media from this URL.", 404)
        return info
    except yt_dlp.utils.DownloadError as exc:
        lower_msg = str(exc).lower()
        cookie_profile_failure_markers = [
            "failed to decrypt",
            "cookie database",
            "could not copy",
            "browser cookies are locked",
            "could not find chrome",
            "chrome cookie",
            "edge cookie",
            "brave cookie",
            "firefox profile",
        ]
        if any(marker in lower_msg for marker in cookie_profile_failure_markers):
            raise AppError(
                "Cookie browser profile is not accessible in this environment. "
                "On Vercel, leave INSTAGRAM_COOKIES_BROWSER empty and use public links only.",
                400,
            ) from exc
        if (
            "private" in lower_msg
            or "login" in lower_msg
            or "log in" in lower_msg
            or "cookies-from-browser" in lower_msg
            or "unauthorized" in lower_msg
            or "forbidden" in lower_msg
            or "not available" in lower_msg
        ):
            has_auth_config = bool(settings.instagram_cookies_file or settings.instagram_cookies_browser)
            if not has_auth_config:
                raise AppError(
                    "Instagram is blocking anonymous access for this link. "
                    "Some public reels/posts still require authenticated sessions.",
                    403,
                ) from exc
            raise AppError(
                "Instagram requires login for this content. Configure cookies via "
                "INSTAGRAM_COOKIES_FILE or INSTAGRAM_COOKIES_BROWSER in backend/.env.",
                403,
            ) from exc
        if "too many requests" in lower_msg or "rate limit" in lower_msg or "try again later" in lower_msg:
            raise AppError("Instagram is rate limiting requests right now. Please retry after a short wait.", 429) from exc
        raise AppError("Unsupported Instagram link or extraction failed.", 400) from exc
    except AppError:
        raise
    except Exception as exc:
        raise AppError("Unexpected error while processing Instagram content.", 500) from exc


def extract_reel(url: str) -> list[MediaItem]:
    cleaned = url.strip()
    if not _is_instagram_url(cleaned) or not _is_reel_url(cleaned):
        raise AppError("Please provide a valid Instagram Reel URL.", 422)

    info = _extract(cleaned)
    entries = info.get("entries") or [info]

    media_items: list[MediaItem] = []
    for idx, entry in enumerate(entries):
        if not entry:
            continue
        video_url = entry.get("url") or entry.get("webpage_url")
        if not video_url:
            continue
        media_items.append(
            MediaItem(
                id=str(entry.get("id") or idx),
                media_type="video",
                media_url=video_url,
                thumbnail_url=entry.get("thumbnail"),
                title=entry.get("title") or "Instagram Reel",
            )
        )

    if not media_items:
        raise AppError("No downloadable reel media found.", 404)

    return media_items


def extract_post(url: str) -> list[MediaItem]:
    cleaned = url.strip()
    if not _is_instagram_url(cleaned) or not _is_post_url(cleaned):
        raise AppError("Please provide a valid Instagram Post URL.", 422)

    info = _extract(cleaned)
    entries = info.get("entries") or [info]

    media_items: list[MediaItem] = []
    for idx, entry in enumerate(entries):
        if not entry:
            continue
        media_url = _resolve_media_url(entry)
        if not media_url:
            continue

        ext = str(entry.get("ext") or "").lower()
        vcodec = str(entry.get("vcodec") or "").lower()
        media_type = "video" if ext in {"mp4", "mov", "m4v", "webm"} or (vcodec and vcodec != "none") else "image"
        media_items.append(
            MediaItem(
                id=str(entry.get("id") or idx),
                media_type=media_type,
                media_url=media_url,
                thumbnail_url=entry.get("thumbnail"),
                title=entry.get("title") or "Instagram Post",
            )
        )

    if not media_items:
        raise AppError("No downloadable post media found.", 404)

    return media_items
