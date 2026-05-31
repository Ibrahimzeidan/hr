"""
Tests for job description parsing functionality.
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from app.ai.jd_parser import parse_job_description
from app.ai.skills import SKILL_TERMS, DEGREE_TERMS


def test_parse_jd_extracts_required_skills():
    jd = """
    We are looking for a Software Engineer with:
    - Python programming skills
    - Experience with React and Node.js
    - Knowledge of PostgreSQL and Redis
    - Familiarity with Docker and AWS
    """
    result = parse_job_description(jd)
    
    assert "Python" in result["required_skills"]
    assert "React" in result["required_skills"]
    assert "Node.Js" in result["required_skills"] or "Node.js" in result["required_skills"]


def test_parse_jd_extracts_experience_requirement():
    jd = "Looking for a developer with 5 years of experience in software development."
    result = parse_job_description(jd)
    
    assert result["min_years"] == 5


def test_parse_jd_extracts_education_terms():
    jd = """
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - Master's degree preferred
    """
    result = parse_job_description(jd)
    
    assert "bachelor" in result["education_terms"]
    assert "master" in result["education_terms"]


def test_parse_jd_extracts_keywords():
    jd = """
    Senior Software Engineer position requiring expertise in 
    machine learning, cloud computing, microservices architecture,
    and agile development methodologies.
    """
    result = parse_job_description(jd)
    
    assert len(result["keywords"]) > 0
    assert isinstance(result["keywords"], list)


def test_parse_jd_handles_minimal_input():
    jd = "Software Developer needed."
    result = parse_job_description(jd)
    
    assert result["text"] == jd
    assert isinstance(result["required_skills"], list)
    assert isinstance(result["keywords"], list)
    assert result["min_years"] == 0


def test_parse_jd_preserves_original_text():
    jd = "Original job description text here."
    result = parse_job_description(jd)
    
    assert result["text"] == jd