"""
Deterministic Resume Scoring Engine

This module implements a deterministic scoring system that calculates
candidate scores (0-100) based on:
- Skills Match (50%)
- Experience Relevance (25%)
- Education Alignment (15%)
- Keyword Similarity (10%)

IMPORTANT: This module ONLY calculates deterministic scores.
AI (Gemini) is NOT used for score calculation - it is only used
for generating explanations, summaries, and insights in the analysis service.
"""

import logging
from typing import Any

from app.ai.jd_parser import parse_job_description
from app.ai.keyword_matcher import overlap_score
from app.ai.resume_parser import parse_resume
from app.ai.semantic_matcher import semantic_similarity

logger = logging.getLogger(__name__)


def score_resume(resume_text: str, jd_text: str) -> dict[str, Any]:
    """
    Calculate deterministic score for a resume against a job description.

    Scoring breakdown:
    - Skills Match: 50% (weighted combination of exact skill match and semantic similarity)
    - Experience Relevance: 25% (based on years of experience vs requirements)
    - Education Alignment: 15% (based on degree/education match)
    - Keyword Similarity: 10% (TF-IDF based keyword overlap)

    Args:
        resume_text: Raw resume text content
        jd_text: Raw job description text content

    Returns:
        Dictionary containing score and analysis results
    """
    try:
        resume = parse_resume(resume_text)
        jd = parse_job_description(jd_text)

        # Calculate skills match score (50%)
        matched, missing, exact_skill_score = overlap_score(jd["required_skills"], resume_text)
        semantic = max(0.0, min(1.0, semantic_similarity(resume_text, jd_text)))
        skill_score = (exact_skill_score * 0.75) + (semantic * 0.25)

        # Calculate experience relevance score (25%)
        experience_score = _experience_score(
            resume["years_experience"], jd["min_years"], semantic
        )

        # Calculate education alignment score (15%)
        education_score = _education_score(
            resume["education"], jd["education_terms"]
        )

        # Calculate keyword similarity score (10%)
        keyword_matched, _, keyword_score = overlap_score(jd["keywords"], resume_text)

        # Calculate total weighted score
        total = (
            (skill_score * 50) +
            (experience_score * 25) +
            (education_score * 15) +
            (keyword_score * 10)
        )

        # Ensure score is within bounds
        final_score = round(min(max(total, 0), 100), 2)

        logger.info(
            f"Scored resume: {resume.get('full_name', 'Unknown')} - "
            f"Score: {final_score}, Skills: {len(matched)}/{len(jd['required_skills'])} matched"
        )

        return {
            "score": final_score,
            "matching_skills": [item.title() for item in matched],
            "missing_skills": [item.title() for item in missing],
            "semantic_similarity": round(semantic * 100, 2),
            "keyword_score": round(keyword_score * 100, 2),
            "explanation": _explain(
                final_score, matched, missing, keyword_matched,
                skill_score, experience_score, education_score
            ),
            # Pass parsed data for analysis service to use with Gemini
            "_resume_data": resume,
            "_jd_data": jd,
        }

    except Exception as e:
        logger.error(f"Error scoring resume: {e}")
        # Return a minimal valid result on error
        return {
            "score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "semantic_similarity": 0,
            "keyword_score": 0,
            "explanation": f"Error processing resume: {str(e)}",
            "_resume_data": {},
            "_jd_data": {},
        }


def _experience_score(candidate_years: int, min_years: int, semantic: float) -> float:
    """
    Calculate experience relevance score (0-1 scale).

    Args:
        candidate_years: Years of experience from candidate's resume
        min_years: Minimum years required by job description
        semantic: Semantic similarity score (0-1)

    Returns:
        Experience score between 0 and 1
    """
    if not min_years:
        # No experience requirement specified
        return 0.75 + (semantic * 0.25)

    # Calculate ratio of candidate experience to required experience
    experience_ratio = min(candidate_years / min_years, 1.0)

    # Weight: 80% based on experience ratio, 20% on semantic match
    return (experience_ratio * 0.8) + (semantic * 0.2)


def _education_score(education: list[str], required_terms: list[str]) -> float:
    """
    Calculate education alignment score (0-1 scale).

    Args:
        education: List of education entries from resume
        required_terms: List of required education terms from JD

    Returns:
        Education score between 0 and 1
    """
    if not required_terms:
        # No education requirements specified
        return 1.0

    if not education:
        return 0.0

    # Check how many required terms are mentioned in education
    haystack = " ".join(education).lower()
    matched_terms = sum(1 for term in required_terms if term.lower() in haystack)

    return matched_terms / len(required_terms)


def _explain(
    total: float,
    matched: list[str],
    missing: list[str],
    keywords: list[str],
    skill_score: float,
    experience_score: float,
    education_score: float,
) -> str:
    """
    Generate a human-readable explanation of the score.

    Args:
        total: Final score (0-100)
        matched: List of matched skills
        missing: List of missing skills
        keywords: List of matched keywords
        skill_score: Calculated skill score (0-1)
        experience_score: Calculated experience score (0-1)
        education_score: Calculated education score (0-1)

    Returns:
        Explanation string
    """
    # Determine overall assessment
    if total >= 80:
        base = "Strong alignment across required skills and role context."
    elif total >= 60:
        base = "Good fit with a few gaps to review during screening."
    elif total >= 40:
        base = "Partial alignment; several requirements need closer review."
    else:
        base = "Limited alignment with job requirements."

    # Add skill match details
    total_required = len(matched) + len(missing)
    skill_detail = f"Matched {len(matched)} of {total_required} required skills."

    # Add component scores
    scores_detail = (
        f" Skills: {skill_score * 100:.0f}%, "
        f"Experience: {experience_score * 100:.0f}%, "
        f"Education: {education_score * 100:.0f}%."
    )

    # Add missing skills
    missing_detail = ""
    if missing:
        missing_str = ", ".join(missing[:5])
        missing_detail = f" Missing: {missing_str}."
    else:
        missing_detail = " All required skills present."

    return f"{base} {skill_detail}{scores_detail}{missing_detail}"