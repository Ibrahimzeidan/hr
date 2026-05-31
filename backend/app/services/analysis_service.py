from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.models import AnalysisResult, Candidate, CandidateSkill, JobDescription
from app.services.candidate_service import get_latest_job_description
from app.services.ranking_service import refresh_ranks
from app.services.scoring_service import score_resume
from app.utils.serializers import candidate_to_out


def analyze_candidates(db: Session, jd_id: int | None, candidate_ids: list[int] | None):
    jd = db.get(JobDescription, jd_id) if jd_id else get_latest_job_description(db)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    query = db.query(Candidate).options(
        joinedload(Candidate.skills).joinedload(CandidateSkill.skill), joinedload(Candidate.analysis)
    )
    if candidate_ids:
        query = query.filter(Candidate.id.in_(candidate_ids))
    candidates = query.all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    for candidate in candidates:
        _save_result(db, candidate, score_resume(candidate.extracted_text, jd.content))
    db.commit()
    refresh_ranks(db)
    rows = query.order_by(Candidate.score.desc()).all()
    return [candidate_to_out(row) for row in rows]


def _save_result(db: Session, candidate: Candidate, score: dict) -> None:
    candidate.score = score["score"]
    result = candidate.analysis or AnalysisResult(candidate_id=candidate.id)
    result.matching_skills = score["matching_skills"]
    result.missing_skills = score["missing_skills"]
    result.semantic_similarity = score["semantic_similarity"]
    result.keyword_score = score["keyword_score"]
    result.explanation = score["explanation"]
    db.add(result)

