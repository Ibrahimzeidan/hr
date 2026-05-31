from app.database.models import Candidate
from app.schemas.candidate import CandidateOut


def candidate_to_out(candidate: Candidate) -> CandidateOut:
    return CandidateOut(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        resume_url=candidate.resume_url,
        score=round(candidate.score or 0, 2),
        rank=candidate.rank,
        created_at=candidate.created_at,
        skills=[link.skill.name for link in candidate.skills],
        analysis=candidate.analysis,
    )

