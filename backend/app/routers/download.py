from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from urllib.parse import urlparse
from urllib.request import Request as UrlRequest, urlopen

from app.schemas.download import DownloadResponse, PostRequest, ReelRequest
from app.services.instagram import extract_post, extract_reel
from app.core.errors import AppError

router = APIRouter(prefix="/download", tags=["download"])


@router.post("/reel", response_model=DownloadResponse)
def download_reel(payload: ReelRequest, request: Request) -> DownloadResponse:
    media = extract_reel(payload.url)
    return DownloadResponse(source=payload.url, media=media, message="Reel extracted successfully")


@router.post("/post", response_model=DownloadResponse)
def download_post(payload: PostRequest, request: Request) -> DownloadResponse:
    media = extract_post(payload.url)
    return DownloadResponse(source=payload.url, media=media, message="Post extracted successfully")


def _validate_cdn_url(url: str) -> None:
    """Ensure the URL points to an allowed Instagram CDN host."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    is_allowed = host.endswith("cdninstagram.com") or host.endswith("fbcdn.net")
    if parsed.scheme not in {"http", "https"} or not is_allowed:
        raise AppError("Unsupported media URL.", 400)


def _fetch_remote(url: str):
    """Fetch a remote URL and return the response object."""
    req = UrlRequest(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return urlopen(req, timeout=30)
    except Exception as exc:
        raise AppError("Failed to fetch remote media.", 502) from exc


@router.get("/stream")
def stream_file(url: str) -> StreamingResponse:
    """Proxy media for inline playback (no attachment header).
    Used by the frontend for <video>/<img> preview so Instagram CDN
    CORS restrictions don't block playback on deployed domains."""
    _validate_cdn_url(url)
    response = _fetch_remote(url)
    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return StreamingResponse(
        response,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.get("/file")
def download_file(url: str, filename: str | None = None) -> StreamingResponse:
    """Proxy media as a downloadable attachment."""
    _validate_cdn_url(url)
    safe_name = (filename or "instagram-media").strip() or "instagram-media"
    response = _fetch_remote(url)
    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return StreamingResponse(
        response,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
        },
    )

