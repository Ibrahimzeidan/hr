from io import BytesIO, StringIO

import pandas as pd
from sqlalchemy.orm import Session, joinedload

from app.database.models import Candidate, CandidateSkill


def candidates_dataframe(db: Session) -> pd.DataFrame:
    rows = (
        db.query(Candidate)
        .options(joinedload(Candidate.skills).joinedload(CandidateSkill.skill), joinedload(Candidate.analysis))
        .order_by(Candidate.rank.asc().nullslast())
        .all()
    )
    return pd.DataFrame([_row(candidate) for candidate in rows])


def csv_bytes(db: Session) -> bytes:
    output = StringIO()
    candidates_dataframe(db).to_csv(output, index=False)
    return output.getvalue().encode("utf-8")


def excel_bytes(db: Session) -> bytes:
    output = BytesIO()
    candidates_dataframe(db).to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output.read()


def _row(candidate: Candidate) -> dict:
    analysis = candidate.analysis
    return {
        "Rank": candidate.rank,
        "Candidate Name": candidate.full_name,
        "Email": candidate.email,
        "Score": candidate.score,
        "Matching Skills": ", ".join(analysis.matching_skills if analysis else []),
        "Missing Skills": ", ".join(analysis.missing_skills if analysis else []),
    }

