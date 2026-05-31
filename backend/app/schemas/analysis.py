from pydantic import BaseModel, Field

from app.schemas.candidate import CandidateOut


class AnalyzeRequest(BaseModel):
    job_description_id: int | None = None
    candidate_ids: list[int] | None = Field(default=None, min_length=1)


class AnalyzeResponse(BaseModel):
    candidates: list[CandidateOut]

