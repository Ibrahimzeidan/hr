from sqlalchemy.orm import Session

from app.database.models import Candidate


def refresh_ranks(db: Session) -> None:
    candidates = db.query(Candidate).order_by(Candidate.score.desc(), Candidate.created_at.asc()).all()
    for index, candidate in enumerate(candidates, start=1):
        candidate.rank = index
    db.commit()

