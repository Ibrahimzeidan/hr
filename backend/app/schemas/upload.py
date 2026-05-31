from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.candidate import CandidateOut


class UploadResponse(BaseModel):
    candidates: list[CandidateOut]


class JobDescriptionOut(BaseModel):
    id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
