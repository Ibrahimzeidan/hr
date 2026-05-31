from io import BytesIO
from re import sub

import cloudinary
import cloudinary.uploader

from app.core.config import get_settings


def upload_resume(filename: str, content: bytes) -> str:
    settings = get_settings()
    safe_name = sub(r"[^a-zA-Z0-9_.-]", "-", filename)
    if not settings.cloudinary_enabled:
        return f"cloudinary-disabled://resume-ranker/{safe_name}"
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    response = cloudinary.uploader.upload(
        BytesIO(content),
        resource_type="raw",
        folder="resume-ranker/resumes",
        public_id=safe_name,
        overwrite=True,
    )
    return response["secure_url"]

