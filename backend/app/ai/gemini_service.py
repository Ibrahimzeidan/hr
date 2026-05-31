"""
Gemini AI Service Layer

This module provides a dedicated service layer for Google Gemini AI interactions.
Gemini is ONLY used for explanations, summaries, missing skills recommendations,
and candidate insights - NOT for calculating or modifying scores.

The service gracefully falls back to deterministic local analysis when:
- GEMINI_API_KEY environment variable is not set
- API calls fail due to rate limiting, timeouts, or other errors
"""

import json
import logging
import os
import time
from datetime import datetime
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 2.0  # seconds

# Cache for Gemini responses to reduce API calls
_response_cache: dict[str, dict[str, Any]] = {}
_cache_timestamps: dict[str, float] = {}
CACHE_TTL = 3600  # 1 hour cache


def _is_cache_valid(key: str) -> bool:
    """Check if cached response is still valid."""
    if key not in _cache_timestamps:
        return False
    age = time.time() - _cache_timestamps[key]
    return age < CACHE_TTL


@lru_cache(maxsize=1)
def _get_api_key() -> str | None:
    """Get Gemini API key from environment variable."""
    return os.getenv("GEMINI_API_KEY")


@lru_cache(maxsize=1)
def _get_model_name() -> str:
    """Get Gemini model name from environment or use default."""
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")


def _get_gemini_client():
    """
    Get Gemini client instance.
    Returns None if API key is not configured.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai
    except ImportError:
        logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")
        return None
    except Exception as e:
        logger.error(f"Failed to configure Gemini client: {e}")
        return None


def _generate_fallback_insights(
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
    matching_skills: list[str],
    missing_skills: list[str],
    score: float
) -> dict[str, Any]:
    """
    Generate deterministic insights when Gemini is unavailable.
    This provides consistent, rule-based analysis.
    """
    # Generate candidate summary
    experience = resume_data.get("years_experience", 0)
    education = resume_data.get("education", [])
    certifications = resume_data.get("certifications", [])

    summary_parts = [f"Candidate with {experience} years of experience."]

    if education:
        education_str = ", ".join(education[:2])
        summary_parts.append(f"Education: {education_str}.")

    skills = resume_data.get("skills", [])
    if skills:
        top_skills = ", ".join(skills[:5])
        summary_parts.append(f"Key skills: {top_skills}.")

    candidate_summary = " ".join(summary_parts)

    # Determine hiring recommendation based on score
    if score >= 85:
        hiring_recommendation = "Strong Hire"
    elif score >= 70:
        hiring_recommendation = "Hire"
    elif score >= 55:
        hiring_recommendation = "Consider"
    elif score >= 40:
        hiring_recommendation = "Weak Match"
    else:
        hiring_recommendation = "Reject"

    # Calculate confidence score based on data completeness
    confidence_factors = []
    if resume_data.get("email"):
        confidence_factors.append(0.2)
    if experience > 0:
        confidence_factors.append(0.2)
    if education:
        confidence_factors.append(0.2)
    if skills:
        confidence_factors.append(0.2)
    if len(matching_skills) > 0:
        confidence_factors.append(0.2)
    confidence_score = min(sum(confidence_factors) * 100, 100)

    # Generate strengths
    strengths = []
    if len(matching_skills) >= 5:
        strengths.append(f"Strong technical skill match with {len(matching_skills)} matching skills")
    if experience >= jd_data.get("min_years", 0):
        strengths.append(f"Meets experience requirement of {jd_data.get('min_years', 0)} years")
    if jd_data.get("education_terms"):
        edu_match = any(term.lower() in " ".join(education).lower() for term in jd_data["education_terms"])
        if edu_match:
            strengths.append("Educational background aligns with job requirements")
    if certifications:
        strengths.append(f"Holds {len(certifications)} certifications")
    if score >= 80:
        strengths.append("High overall compatibility score")

    # Generate weaknesses
    weaknesses = []
    if missing_skills:
        weaknesses.append(f"Missing {len(missing_skills)} required skills: {', '.join(missing_skills[:3])}")
    if experience < jd_data.get("min_years", 0):
        weaknesses.append(f"Below required experience level ({experience} vs {jd_data.get('min_years', 0)} years)")
    if not resume_data.get("email"):
        weaknesses.append("Missing contact email")
    if len(skills) < 3:
        weaknesses.append("Limited technical skills listed")

    # Generate recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(f"Consider upskilling in: {', '.join(missing_skills[:3])}")
    if experience < jd_data.get("min_years", 0):
        recommendations.append("Gain more relevant work experience")
    if not certifications and jd_data.get("education_terms"):
        recommendations.append("Consider obtaining relevant certifications")
    recommendations.append("Review project portfolio for practical skill demonstration")

    # Generate explanation
    explanation = (
        f"Score: {score}/100. "
        f"Matched {len(matching_skills)} out of {len(matching_skills) + len(missing_skills)} required skills. "
    )
    if strengths:
        explanation += f"Strengths include: {strengths[0]}. "
    if weaknesses:
        explanation += f"Areas of concern: {weaknesses[0]}."

    return {
        "candidate_summary": candidate_summary,
        "hiring_recommendation": hiring_recommendation,
        "confidence_score": round(confidence_score, 2),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "explanation": explanation,
        "ai_provider": "local_fallback",
        "ai_model": None,
    }


async def generate_candidate_insights(
    resume_text: str,
    jd_text: str,
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
    matching_skills: list[str],
    missing_skills: list[str],
    score: float,
) -> dict[str, Any]:
    """
    Generate comprehensive candidate insights using Gemini AI.

    This function uses Gemini to provide:
    - Candidate summary
    - Hiring recommendation
    - Confidence score
    - Strengths and weaknesses
    - Recommendations
    - Detailed explanation

    Falls back to deterministic local analysis if Gemini is unavailable.

    Args:
        resume_text: Raw resume text
        jd_text: Raw job description text
        resume_data: Parsed resume data
        jd_data: Parsed job description data
        matching_skills: Skills that match between resume and JD
        missing_skills: Required skills missing from resume
        score: Deterministic score (0-100) calculated by scoring engine

    Returns:
        Dictionary containing all insight fields
    """
    # Create cache key
    cache_key = f"{hash(resume_text)}_{hash(jd_text)}_{score}"

    # Check cache first
    if _is_cache_valid(cache_key):
        logger.info("Returning cached Gemini insights")
        return _response_cache[cache_key]

    # Try Gemini first
    genai = _get_gemini_client()
    if genai is not None:
        try:
            result = await _generate_gemini_insights(
                genai, resume_text, jd_text, resume_data, jd_data,
                matching_skills, missing_skills, score
            )
            if result:
                # Cache the result
                _response_cache[cache_key] = result
                _cache_timestamps[cache_key] = time.time()
                return result
        except Exception as e:
            logger.warning(f"Gemini insights generation failed, using fallback: {e}")

    # Use fallback
    logger.info("Using deterministic local fallback for insights")
    fallback_result = _generate_fallback_insights(
        resume_data, jd_data, matching_skills, missing_skills, score
    )
    return fallback_result


async def _generate_gemini_insights(
    genai: Any,
    resume_text: str,
    jd_text: str,
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
    matching_skills: list[str],
    missing_skills: list[str],
    score: float,
) -> dict[str, Any] | None:
    """
    Generate insights using Gemini API with retry logic.
    """
    model_name = _get_model_name()

    for attempt in range(MAX_RETRIES):
        try:
            model = genai.GenerativeModel(model_name)

            prompt = _build_gemini_prompt(
                resume_text, jd_text, resume_data, jd_data,
                matching_skills, missing_skills, score
            )

            # Generate response with timeout
            response = await _call_with_timeout(model.generate_content, prompt)

            if response and response.text:
                return _parse_gemini_response(response.text, model_name)

        except Exception as e:
            logger.warning(f"Gemini API attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await _async_sleep(RETRY_DELAY * (attempt + 1))
            continue

    return None


def _build_gemini_prompt(
    resume_text: str,
    jd_text: str,
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
    matching_skills: list[str],
    missing_skills: list[str],
    score: float,
) -> str:
    """Build the prompt for Gemini API."""

    prompt = f"""You are an expert HR analyst reviewing a candidate's resume against a job description.
Provide a comprehensive analysis in JSON format.

IMPORTANT: The score ({score}/100) has already been calculated by a deterministic scoring engine.
Do NOT calculate or modify the score. Use it as-is in your analysis.

RESUME DATA:
- Name: {resume_data.get('full_name', 'N/A')}
- Email: {resume_data.get('email', 'N/A')}
- Years of Experience: {resume_data.get('years_experience', 0)}
- Education: {', '.join(resume_data.get('education', []))}
- Skills: {', '.join(resume_data.get('skills', []))}
- Certifications: {', '.join(resume_data.get('certifications', []))}

JOB REQUIREMENTS:
- Required Skills: {', '.join(jd_data.get('required_skills', []))}
- Minimum Experience: {jd_data.get('min_years', 0)} years
- Education Requirements: {', '.join(jd_data.get('education_terms', []))}

MATCH ANALYSIS:
- Score: {score}/100
- Matching Skills ({len(matching_skills)}): {', '.join(matching_skills)}
- Missing Skills ({len(missing_skills)}): {', '.join(missing_skills)}

Provide your analysis in the following JSON format (no markdown, just raw JSON):
{{
    "candidate_summary": "2-3 sentence professional summary of the candidate",
    "hiring_recommendation": "Strong Hire | Hire | Consider | Weak Match | Reject",
    "confidence_score": 0-100,
    "strengths": ["strength 1", "strength 2", ...],
    "weaknesses": ["weakness 1", "weakness 2", ...],
    "recommendations": ["recommendation 1", "recommendation 2", ...],
    "explanation": "Detailed explanation of the analysis and reasoning"
}}

Ensure the JSON is valid and can be parsed directly."""

    return prompt


async def _call_with_timeout(func: callable, *args, **kwargs) -> Any:
    """Call a function with timeout handling."""
    import asyncio
    import google.generativeai as genai

    try:
        # Use asyncio.wait_for for timeout
        return await asyncio.wait_for(func(*args, **kwargs), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds")
        raise
    except genai.types.BlockedPromptException:
        logger.warning("Prompt was blocked by safety filters")
        raise
    except genai.types.StopCandidateException:
        logger.warning("Generation was stopped")
        raise


async def _async_sleep(seconds: float) -> None:
    """Async sleep helper."""
    import asyncio
    await asyncio.sleep(seconds)


def _parse_gemini_response(response_text: str, model_name: str) -> dict[str, Any]:
    """Parse and validate Gemini response."""
    # Clean up response (remove markdown code blocks if present)
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        # Try to extract JSON from text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                data = json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                logger.error("Could not extract JSON from response")
                raise

    # Validate required fields and provide defaults
    result = {
        "candidate_summary": data.get("candidate_summary", "No summary available."),
        "hiring_recommendation": data.get("hiring_recommendation", "Consider"),
        "confidence_score": min(100, max(0, data.get("confidence_score", 70))),
        "strengths": data.get("strengths", []),
        "weaknesses": data.get("weaknesses", []),
        "recommendations": data.get("recommendations", []),
        "explanation": data.get("explanation", "Analysis completed."),
        "ai_provider": "google_gemini",
        "ai_model": model_name,
    }

    # Validate hiring_recommendation value
    valid_recommendations = ["Strong Hire", "Hire", "Consider", "Weak Match", "Reject"]
    if result["hiring_recommendation"] not in valid_recommendations:
        result["hiring_recommendation"] = "Consider"

    return result


def clear_cache():
    """Clear the response cache."""
    _response_cache.clear()
    _cache_timestamps.clear()


def is_gemini_available() -> bool:
    """Check if Gemini AI is available (API key configured)."""
    return _get_api_key() is not None


def get_gemini_status() -> dict[str, Any]:
    """Get the current status of Gemini service."""
    api_key = _get_api_key()
    model = _get_model_name()
    return {
        "available": api_key is not None,
        "model": model if api_key else None,
        "cache_size": len(_response_cache),
    }