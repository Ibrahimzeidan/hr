from pathlib import Path

import bleach
from fastapi import HTTPException, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings


limiter = Limiter(key_func=get_remote_address)
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


def sanitize_text(value: str) -> str:
    return bleach.clean(value or "", tags=[], strip=True).strip()


def validate_upload(file: UploadFile, size: int) -> None:
    suffix = Path(file.filename or "").suffix.lower()
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported file type: {suffix}")
    if size > max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds upload limit")

