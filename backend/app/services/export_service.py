"""
Export Service

Provides functionality to export candidate data to CSV and Excel formats.
Includes all candidate information including Gemini-enhanced insights.
"""

import logging
from io import BytesIO, StringIO
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session, joinedload

from app.database.models import Candidate, CandidateSkill

logger = logging.getLogger(__name__)


def candidates_dataframe(db: Session) -> pd.DataFrame:
    """
    Get all candidates as a pandas DataFrame.

    Includes all candidate information and analysis results.

    Args:
        db: Database session

    Returns:
        DataFrame with candidate data
    """
    rows = (
        db.query(Candidate)
        .options(
            joinedload(Candidate.skills).joinedload(CandidateSkill.skill),
            joinedload(Candidate.analysis)
        )
        .order_by(Candidate.rank.asc().nullslast())
        .all()
    )
    return pd.DataFrame([_row_to_dict(candidate) for candidate in rows])


def csv_bytes(db: Session) -> bytes:
    """
    Export candidates to CSV format.

    Args:
        db: Database session

    Returns:
        CSV content as bytes
    """
    output = StringIO()
    df = candidates_dataframe(db)
    df.to_csv(output, index=False)
    csv_content = output.getvalue()
    logger.info(f"Exported {len(df)} candidates to CSV")
    return csv_content.encode("utf-8")


def excel_bytes(db: Session) -> bytes:
    """
    Export candidates to Excel format.

    Creates an Excel file with multiple sheets:
    - Candidates: Main candidate data
    - Skills: Detailed skills breakdown
    - Analysis: Detailed analysis results

    Args:
        db: Database session

    Returns:
        Excel file content as bytes
    """
    output = BytesIO()
    df = candidates_dataframe(db)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Main candidates sheet
        df.to_excel(writer, index=False, sheet_name="Candidates")

        # Create a skills breakdown sheet
        skills_data = []
        for _, row in df.iterrows():
            if row.get("Matching Skills"):
                for skill in str(row["Matching Skills"]).split(", "):
                    if skill and skill != "nan":
                        skills_data.append({
                            "Candidate": row.get("Candidate Name", ""),
                            "Skill": skill,
                            "Type": "Matched"
                        })
            if row.get("Missing Skills"):
                for skill in str(row["Missing Skills"]).split(", "):
                    if skill and skill != "nan":
                        skills_data.append({
                            "Candidate": row.get("Candidate Name", ""),
                            "Skill": skill,
                            "Type": "Missing"
                        })

        if skills_data:
            pd.DataFrame(skills_data).to_excel(
                writer, index=False, sheet_name="Skills"
            )

    output.seek(0)
    logger.info(f"Exported {len(df)} candidates to Excel")
    return output.read()


def _row_to_dict(candidate: Candidate) -> dict[str, Any]:
    """
    Convert a candidate record to a dictionary for export.

    Args:
        candidate: Candidate ORM object

    Returns:
        Dictionary with all candidate data
    """
    analysis = candidate.analysis

    return {
        "Rank": candidate.rank,
        "Candidate Name": candidate.full_name,
        "Email": candidate.email or "",
        "Phone": candidate.phone or "",
        "Score": candidate.score,
        "Matching Skills": ", ".join(analysis.matching_skills if analysis else []),
        "Missing Skills": ", ".join(analysis.missing_skills if analysis else []),
        "Semantic Similarity": analysis.semantic_similarity if analysis else 0,
        "Keyword Score": analysis.keyword_score if analysis else 0,
        # Gemini-enhanced fields
        "Candidate Summary": analysis.candidate_summary if analysis else "",
        "Hiring Recommendation": analysis.hiring_recommendation if analysis else "",
        "Confidence Score": analysis.confidence_score if analysis else 0,
        "Strengths": ", ".join(analysis.strengths if analysis else []),
        "Weaknesses": ", ".join(analysis.weaknesses if analysis else []),
        "Recommendations": ", ".join(analysis.recommendations if analysis else []),
        "AI Provider": analysis.ai_provider if analysis else "",
        "AI Model": analysis.ai_model if analysis else "",
        "Explanation": analysis.explanation if analysis else "",
        "Resume URL": candidate.resume_url,
        "Created At": candidate.created_at.isoformat() if candidate.created_at else "",
    }


def export_filtered_candidates(
    db: Session,
    candidate_ids: list[int],
) -> tuple[bytes, bytes]:
    """
    Export a filtered list of candidates.

    Args:
        db: Database session
        candidate_ids: List of candidate IDs to export

    Returns:
        Tuple of (csv_bytes, excel_bytes)
    """
    candidates = (
        db.query(Candidate)
        .options(
            joinedload(Candidate.skills).joinedload(CandidateSkill.skill),
            joinedload(Candidate.analysis)
        )
        .filter(Candidate.id.in_(candidate_ids))
        .all()
    )

    df = pd.DataFrame([_row_to_dict(c) for c in candidates])

    # CSV export
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    csv_result = csv_output.getvalue().encode("utf-8")

    # Excel export
    excel_output = BytesIO()
    with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Candidates")
    excel_output.seek(0)
    excel_result = excel_output.read()

    logger.info(f"Exported {len(candidates)} filtered candidates")
    return csv_result, excel_result