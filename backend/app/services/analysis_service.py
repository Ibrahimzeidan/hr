"""
Analysis Service

This service orchestrates the candidate analysis workflow, including:
- Running deterministic scoring
- Generating AI-powered insights using Gemini
- Saving analysis results to the database
- Refreshing candidate rankings
"""

import asyncio
import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.ai.gemini_service import generate_candidate_insights, is_gemini_available
from app.database.models import AnalysisResult, Candidate, CandidateSkill, JobDescription
from app.services.candidate_service import get_latest_job_description
from app.services.ranking_service import refresh_ranks
from app.services.scoring_service import score_resume
from app.utils.serializers import candidate_to_out

logger = logging.getLogger(__name__)


def analyze_candidates(db: Session, jd_id: int | None, candidate_ids: list[int] | None):
    """
    Analyze candidates against a job description.

    This function:
    1. Retrieves the job description
    2. Scores each candidate using the deterministic scoring engine
    3. Generates AI-powered insights using Gemini (or fallback)
    4. Saves all results to the database
    5. Refreshes candidate rankings

    Args:
        db: Database session
        jd_id: Optional job description ID (uses latest if not provided)
        candidate_ids: Optional list of candidate IDs to analyze (analyzes all if not provided)
    """
    # Get job description
    jd = db.get(JobDescription, jd_id) if jd_id else get_latest_job_description(db)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Query candidates
    query = db.query(Candidate).options(
        joinedload(Candidate.skills).joinedload(CandidateSkill.skill),
        joinedload(Candidate.analysis)
    )
    if candidate_ids:
        query = query.filter(Candidate.id.in_(candidate_ids))
    candidates = query.all()

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")

    # Check Gemini availability
    gemini_available = is_gemini_available()
    if gemini_available:
        logger.info("Gemini AI is available - generating enhanced insights")
    else:
        logger.warning("Gemini AI not available - using deterministic fallback for insights")

    # Process each candidate
    for candidate in candidates:
        try:
            # Get deterministic score
            score_result = score_resume(candidate.extracted_text, jd.content)

            # Generate AI insights
            insights = asyncio.run(
                generate_candidate_insights(
                    resume_text=candidate.extracted_text,
                    jd_text=jd.content,
                    resume_data=score_result.get("_resume_data", {}),
                    jd_data=score_result.get("_jd_data", {}),
                    matching_skills=score_result["matching_skills"],
                    missing_skills=score_result["missing_skills"],
                    score=score_result["score"],
                )
            )

            # Merge score result with insights
            merged_result = {**score_result, **insights}

            # Save to database
            _save_result(db, candidate, merged_result)

        except Exception as e:
            logger.error(f"Error analyzing candidate {candidate.id}: {e}")
            # Continue with other candidates even if one fails
            continue

    # Commit all changes
    db.commit()

    # Refresh rankings
    refresh_ranks(db)

    # Return updated candidates
    rows = query.order_by(Candidate.score.desc()).all()
    return [candidate_to_out(row) for row in rows]


def analyze_single_candidate(
    db: Session,
    candidate: Candidate,
    jd: JobDescription,
) -> dict[str, Any]:
    """
    Analyze a single candidate against a job description.

    This is useful for real-time analysis of individual candidates.

    Args:
        db: Database session
        candidate: Candidate to analyze
        jd: Job description to compare against

    Returns:
        Dictionary containing analysis results
    """
    # Get deterministic score
    score_result = score_resume(candidate.extracted_text, jd.content)

    # Generate AI insights
    insights = asyncio.run(
        generate_candidate_insights(
            resume_text=candidate.extracted_text,
            jd_text=jd.content,
            resume_data=score_result.get("_resume_data", {}),
            jd_data=score_result.get("_jd_data", {}),
            matching_skills=score_result["matching_skills"],
            missing_skills=score_result["missing_skills"],
            score=score_result["score"],
        )
    )

    # Merge results
    merged_result = {**score_result, **insights}

    # Save to database
    _save_result(db, candidate, merged_result)
    db.commit()

    # Refresh rankings
    refresh_ranks(db)

    return merged_result


def _save_result(db: Session, candidate: Candidate, score: dict) -> None:
    """
    Save analysis results to the database.

    Args:
        db: Database session
        candidate: Candidate to update
        score: Analysis results dictionary
    """
    # Update candidate score
    candidate.score = score["score"]

    # Get or create analysis result
    result = candidate.analysis or AnalysisResult(candidate_id=candidate.id)

    # Update standard fields
    result.matching_skills = score.get("matching_skills", [])
    result.missing_skills = score.get("missing_skills", [])
    result.semantic_similarity = score.get("semantic_similarity", 0)
    result.keyword_score = score.get("keyword_score", 0)
    result.explanation = score.get("explanation", "")

    # Update Gemini-enhanced fields
    result.candidate_summary = score.get("candidate_summary", "")
    result.hiring_recommendation = score.get("hiring_recommendation", "Consider")
    result.confidence_score = score.get("confidence_score", 0)
    result.strengths = score.get("strengths", [])
    result.weaknesses = score.get("weaknesses", [])
    result.recommendations = score.get("recommendations", [])
    result.ai_provider = score.get("ai_provider")
    result.ai_model = score.get("ai_model")

    db.add(result)


def get_analysis_summary(db: Session, candidate_ids: list[int] | None = None) -> dict[str, Any]:
    """
    Get a summary of analysis results.

    Args:
        db: Database session
        candidate_ids: Optional list of candidate IDs to include

    Returns:
        Summary statistics
    """
    query = db.query(AnalysisResult).join(Candidate)
    if candidate_ids:
        query = query.filter(Candidate.id.in_(candidate_ids))

    results = query.all()

    if not results:
        return {"total": 0}

    scores = [r.candidate.score for r in results]
    recommendations = [r.hiring_recommendation for r in results if r.hiring_recommendation]

    return {
        "total": len(results),
        "average_score": round(sum(scores) / len(scores), 2),
        "min_score": min(scores),
        "max_score": max(scores),
        "recommendation_distribution": {
            rec: recommendations.count(rec)
            for rec in set(recommendations)
        },
        "gemini_usage": sum(1 for r in results if r.ai_provider == "google_gemini"),
        "fallback_usage": sum(1 for r in results if r.ai_provider == "local_fallback"),
    }