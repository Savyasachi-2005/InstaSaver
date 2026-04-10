from collections import defaultdict, deque
from time import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import AppError
from app.routers.download import router as download_router

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rate_window_by_ip: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def basic_rate_limiter(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time()
    one_minute_ago = now - 60

    history = _rate_window_by_ip[client_ip]
    while history and history[0] < one_minute_ago:
        history.popleft()

    if len(history) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down and retry in a minute."},
        )

    history.append(now)
    return await call_next(request)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(download_router, prefix=settings.api_prefix)
