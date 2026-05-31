from fastapi import APIRouter, HTTPException, Query, Request

from app.api.dependencies.database import DbSession
from app.core.security import limiter
from app.schemas.candidate import CandidateList, CandidateOut
from app.services.candidate_service import get_candidate, list_candidates
from app.utils.serializers import candidate_to_out

router = APIRouter(tags=["candidates"])


@router.get("/candidates", response_model=CandidateList)
@limiter.limit("90/minute")
def read_candidates(
    request: Request,
    db: DbSession,
    search: str | None = None,
    min_score: float | None = Query(default=None, ge=0, le=100),
    sort: str = Query(default="score", pattern="^(score|name|created)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    items, total = list_candidates(db, search, min_score, sort, page, limit)
    return CandidateList(items=items, total=total, page=page, limit=limit)


@router.get("/candidate/{candidate_id}", response_model=CandidateOut)
@limiter.limit("120/minute")
def read_candidate(request: Request, candidate_id: int, db: DbSession):
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_to_out(candidate)

