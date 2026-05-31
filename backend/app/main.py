from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import analysis, candidates, export, upload
from app.core.config import get_settings
from app.core.security import limiter
from app.schemas.common import Message

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=Message)
def health() -> Message:
    return Message(message="ok")


app.include_router(candidates.router)
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(export.router)
