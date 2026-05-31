"""
Tests for the deterministic scoring engine.
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from app.services.scoring_service import score_resume, _experience_score, _education_score


def test_score_resume_returns_valid_range():
    resume = """
    Test Candidate
    test@example.com
    3 years Python, JavaScript, React
    Bachelor Computer Science
    """
    jd = "Need Python, JavaScript, React developer with 2 years experience."
    
    result = score_resume(resume, jd)
    
    assert 0 <= result["score"] <= 100
    assert isinstance(result["score"], float)


def test_score_resume_detects_matches_and_gaps():
    resume = """
    Jane Doe
    jane@example.com
    Software Engineer with 4 years of Python, React, FastAPI, PostgreSQL and Docker.
    Education: Bachelor in Computer Science
    """
    jd = "Need 3 years Python, React, FastAPI, PostgreSQL, Docker, AWS. Bachelor required."
    
    result = score_resume(resume, jd)
    
    assert result["score"] >= 70
    assert "Python" in result["matching_skills"]
    assert "Aws" in result["missing_skills"] or "AWS" in result["missing_skills"]
    assert 0 <= result["semantic_similarity"] <= 100


def test_score_resume_weights_skills_heavily():
    """Skills should be 50% of the score."""
    resume = """
    Developer
    dev@example.com
    5 years experience with Python, Java, JavaScript, React, Node.js, 
    PostgreSQL, MongoDB, Docker, Kubernetes, AWS, GCP
    Bachelor Computer Science
    """
    jd = "Need Python, Java, JavaScript, React, Node.js, PostgreSQL, Docker, AWS developer."
    
    result = score_resume(resume, jd)
    
    # High skill match should result in good score
    assert result["score"] >= 75
    assert len(result["matching_skills"]) >= 6


def test_score_resume_experience_factor():
    """Experience should affect the score."""
    resume_experienced = """
    Senior Dev
    senior@example.com
    10 years Python development experience.
    """
    resume_junior = """
    Junior Dev
    junior@example.com
    1 year Python development experience.
    """
    jd = "Need Python developer with 5 years experience."
    
    result_experienced = score_resume(resume_experienced, jd)
    result_junior = score_resume(resume_junior, jd)
    
    # Experienced candidate should score higher (all else being equal)
    # Note: This is a simplified test - in reality other factors also matter
    assert result_experienced["score"] >= result_junior["score"]


def test_experience_score_calculation():
    """Test the experience score helper function."""
    # Candidate meets requirement exactly
    score = _experience_score(5, 5, 0.8)
    assert 0.7 <= score <= 1.0
    
    # Candidate exceeds requirement
    score = _experience_score(10, 5, 0.8)
    assert score >= 0.8
    
    # Candidate below requirement
    score = _experience_score(2, 5, 0.5)
    assert score < 0.5
    
    # No requirement specified
    score = _experience_score(3, 0, 0.5)
    assert score >= 0.7


def test_education_score_calculation():
    """Test the education score helper function."""
    # Perfect match
    score = _education_score(["Bachelor Computer Science"], ["bachelor"])
    assert score == 1.0
    
    # Partial match
    score = _education_score(["Associate Degree"], ["bachelor", "master"])
    assert score == 0.0  # No match for bachelor or master
    
    # No requirements
    score = _education_score(["High School"], [])
    assert score == 1.0
    
    # No education provided
    score = _education_score([], ["bachelor"])
    assert score == 0.0


def test_score_resume_explanation():
    """Test that explanation is generated."""
    resume = """
    Developer
    dev@test.com
    Python, JavaScript experience.
    """
    jd = "Need Python developer."
    
    result = score_resume(resume, jd)
    
    assert result["explanation"] != ""
    assert isinstance(result["explanation"], str)


def test_score_resume_handles_empty_input():
    """Test graceful handling of empty inputs."""
    result = score_resume("", "")
    
    assert result["score"] == 0
    assert result["matching_skills"] == []
    assert result["missing_skills"] == []


def test_score_resume_deterministic():
    """Same input should produce same output (deterministic)."""
    resume = """
    Consistent Candidate
    consistent@example.com
    5 years Python, React, AWS experience.
    Bachelor Computer Science
    """
    jd = "Need Python, React, AWS developer with Bachelor's degree."
    
    result1 = score_resume(resume, jd)
    result2 = score_resume(resume, jd)
    
    assert result1["score"] == result2["score"]
    assert result1["matching_skills"] == result2["matching_skills"]
    assert result1["missing_skills"] == result2["missing_skills"]