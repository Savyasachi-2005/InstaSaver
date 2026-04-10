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


@router.get("/file")
def download_file(url: str, filename: str | None = None) -> StreamingResponse:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    is_allowed = host.endswith("cdninstagram.com") or host.endswith("fbcdn.net")

    if parsed.scheme not in {"http", "https"} or not is_allowed:
        raise AppError("Unsupported media URL for direct download.", 400)

    safe_name = (filename or "instagram-media").strip() or "instagram-media"
    req = UrlRequest(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        response = urlopen(req, timeout=30)
    except Exception as exc:
        raise AppError("Failed to fetch remote media for download.", 502) from exc

    content_type = response.headers.get("Content-Type", "application/octet-stream")
    disposition = f'attachment; filename="{safe_name}"'

    return StreamingResponse(
        response,
        media_type=content_type,
        headers={"Content-Disposition": disposition},
    )
