from fastapi import APIRouter, Request

from app.api.dependencies.database import DbSession
from app.core.security import limiter
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import analyze_candidates

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("20/minute")
def analyze(request: Request, payload: AnalyzeRequest, db: DbSession):
    candidates = analyze_candidates(db, payload.job_description_id, payload.candidate_ids)
    return AnalyzeResponse(candidates=candidates)

