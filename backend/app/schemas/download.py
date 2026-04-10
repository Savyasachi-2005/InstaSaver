from pydantic import BaseModel, Field


class ReelRequest(BaseModel):
    url: str = Field(min_length=10, max_length=500)


class PostRequest(BaseModel):
    url: str = Field(min_length=10, max_length=500)


class MediaItem(BaseModel):
    id: str
    media_type: str
    media_url: str
    thumbnail_url: str | None = None
    title: str | None = None


class DownloadResponse(BaseModel):
    source: str
    media: list[MediaItem]
    message: str | None = None
