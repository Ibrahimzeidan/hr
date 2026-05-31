import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from app.services.scoring_service import score_resume


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
    assert "Aws" in result["missing_skills"]
    assert 0 <= result["semantic_similarity"] <= 100

