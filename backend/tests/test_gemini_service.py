"""
Tests for the Gemini AI service layer.
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

# Ensure no API key is set for testing fallback behavior
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

from app.ai.gemini_service import (
    generate_candidate_insights,
    _generate_fallback_insights,
    is_gemini_available,
    get_gemini_status,
    clear_cache,
)


def test_is_gemini_available_returns_false_without_key():
    """Test that Gemini is not available when API key is not set."""
    assert is_gemini_available() is False


def test_get_gemini_status_without_key():
    """Test Gemini status when no API key is configured."""
    status = get_gemini_status()
    assert status["available"] is False
    assert status["model"] is None


def test_fallback_insights_returns_valid_structure():
    """Test that fallback insights have the correct structure."""
    resume_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "years_experience": 5,
        "education": ["Bachelor Computer Science"],
        "skills": ["Python", "JavaScript", "React"],
        "certifications": ["AWS Certified"],
    }
    jd_data = {
        "required_skills": ["Python", "React", "AWS"],
        "min_years": 3,
        "education_terms": ["bachelor"],
    }
    matching_skills = ["Python", "React"]
    missing_skills = ["AWS"]
    score = 75.0
    
    insights = _generate_fallback_insights(
        resume_data, jd_data, matching_skills, missing_skills, score
    )
    
    # Verify all required fields are present
    assert "candidate_summary" in insights
    assert "hiring_recommendation" in insights
    assert "confidence_score" in insights
    assert "strengths" in insights
    assert "weaknesses" in insights
    assert "recommendations" in insights
    assert "explanation" in insights
    assert "ai_provider" in insights
    assert "ai_model" in insights


def test_fallback_insights_hiring_recommendation_based_on_score():
    """Test that hiring recommendation is based on score thresholds."""
    resume_data = {"years_experience": 5, "education": [], "skills": [], "certifications": [], "email": "test@example.com"}
    jd_data = {"required_skills": [], "min_years": 0, "education_terms": []}
    
    # Strong Hire (>= 85)
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 90)
    assert insights["hiring_recommendation"] == "Strong Hire"
    
    # Hire (>= 70)
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 75)
    assert insights["hiring_recommendation"] == "Hire"
    
    # Consider (>= 55)
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 60)
    assert insights["hiring_recommendation"] == "Consider"
    
    # Weak Match (>= 40)
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 45)
    assert insights["hiring_recommendation"] == "Weak Match"
    
    # Reject (< 40)
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 30)
    assert insights["hiring_recommendation"] == "Reject"


def test_fallback_insights_confidence_score_range():
    """Test that confidence score is within valid range."""
    resume_data = {"years_experience": 5, "education": [], "skills": [], "certifications": [], "email": "test@example.com"}
    jd_data = {"required_skills": [], "min_years": 0, "education_terms": []}
    
    insights = _generate_fallback_insights(resume_data, jd_data, [], [], 75)
    
    assert 0 <= insights["confidence_score"] <= 100


def test_fallback_insights_generates_strengths():
    """Test that strengths are generated based on candidate data."""
    resume_data = {
        "years_experience": 5,
        "education": ["Bachelor Computer Science"],
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
        "certifications": ["AWS Certified"],
        "email": "test@example.com",
    }
    jd_data = {
        "required_skills": ["Python", "React"],
        "min_years": 3,
        "education_terms": ["bachelor"],
    }
    
    insights = _generate_fallback_insights(
        resume_data, jd_data, ["Python", "React"], [], 85
    )
    
    assert len(insights["strengths"]) > 0
    # Should mention skill match
    assert any("skill" in s.lower() for s in insights["strengths"])


def test_fallback_insights_generates_weaknesses_for_missing_skills():
    """Test that weaknesses are generated when skills are missing."""
    resume_data = {
        "years_experience": 2,
        "education": [],
        "skills": ["Python"],
        "certifications": [],
        "email": "test@example.com",
    }
    jd_data = {
        "required_skills": ["Python", "React", "AWS", "Docker"],
        "min_years": 5,
        "education_terms": [],
    }
    
    insights = _generate_fallback_insights(
        resume_data, jd_data, ["Python"], ["React", "AWS", "Docker"], 40
    )
    
    assert len(insights["weaknesses"]) > 0
    # Should mention missing skills
    assert any("missing" in w.lower() for w in insights["weaknesses"])


def test_fallback_insights_generates_recommendations():
    """Test that recommendations are generated."""
    resume_data = {
        "years_experience": 2,
        "education": [],
        "skills": ["Python"],
        "certifications": [],
        "email": "test@example.com",
    }
    jd_data = {
        "required_skills": ["Python", "React"],
        "min_years": 5,
        "education_terms": [],
    }
    
    insights = _generate_fallback_insights(
        resume_data, jd_data, ["Python"], ["React"], 50
    )
    
    assert len(insights["recommendations"]) > 0
    # Should mention upskilling
    assert any("upskill" in r.lower() or "skill" in r.lower() for r in insights["recommendations"])


def test_generate_candidate_insights_uses_fallback_without_api_key():
    """Test that insights generation falls back to local analysis."""
    resume_text = "Test resume with Python experience"
    jd_text = "Looking for Python developer"
    resume_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "years_experience": 3,
        "education": ["Bachelor"],
        "skills": ["Python"],
        "certifications": [],
    }
    jd_data = {
        "required_skills": ["Python"],
        "min_years": 2,
        "education_terms": ["bachelor"],
    }
    
    import asyncio
    insights = asyncio.run(
        generate_candidate_insights(
            resume_text, jd_text, resume_data, jd_data,
            ["Python"], [], 80
        )
    )
    
    # Should return valid insights from fallback
    assert insights["ai_provider"] == "local_fallback"
    assert insights["candidate_summary"] != ""
    assert insights["hiring_recommendation"] in ["Strong Hire", "Hire", "Consider", "Weak Match", "Reject"]


def test_clear_cache():
    """Test that cache can be cleared."""
    # Just verify it doesn't raise an exception
    clear_cache()


def test_fallback_insights_deterministic():
    """Test that fallback insights are deterministic (same input = same output)."""
    resume_data = {
        "full_name": "Deterministic User",
        "email": "det@example.com",
        "years_experience": 5,
        "education": ["Bachelor Computer Science"],
        "skills": ["Python", "React"],
        "certifications": [],
    }
    jd_data = {
        "required_skills": ["Python", "React"],
        "min_years": 3,
        "education_terms": ["bachelor"],
    }
    
    insights1 = _generate_fallback_insights(resume_data, jd_data, ["Python", "React"], [], 85)
    insights2 = _generate_fallback_insights(resume_data, jd_data, ["Python", "React"], [], 85)
    
    assert insights1["candidate_summary"] == insights2["candidate_summary"]
    assert insights1["hiring_recommendation"] == insights2["hiring_recommendation"]
    assert insights1["confidence_score"] == insights2["confidence_score"]