"""
Tests for resume parsing functionality.
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from app.ai.resume_parser import parse_resume
from app.ai.keyword_matcher import extract_skills, extract_keywords


def test_parse_resume_extracts_basic_info():
    resume = """
    Jane Doe
    jane@example.com
    +1-555-123-4567
    
    Software Engineer with 4 years of experience.
    
    Education: Bachelor in Computer Science
    """
    result = parse_resume(resume)
    
    assert result["full_name"] == "Jane Doe"
    assert result["email"] == "jane@example.com"
    assert result["phone"] == "+1-555-123-4567"


def test_parse_resume_extracts_skills():
    resume = """
    John Smith
    john@test.com
    
    Experienced with Python, JavaScript, React, Docker, and AWS.
    """
    result = parse_resume(resume)
    
    assert "Python" in result["skills"]
    assert "Javascript" in result["skills"] or "JavaScript" in result["skills"]
    assert "React" in result["skills"]
    assert "Docker" in result["skills"]
    assert "Aws" in result["skills"] or "AWS" in result["skills"]


def test_parse_resume_extracts_experience():
    resume = """
    Test Candidate
    test@email.com
    
    5 years of experience in software development.
    
    Experience:
    Senior Developer at Tech Corp
    """
    result = parse_resume(resume)
    
    assert result["years_experience"] == 5


def test_parse_resume_extracts_education():
    resume = """
    Graduate Student
    grad@university.edu
    
    Education:
    Master of Science in Computer Science
    Stanford University
    """
    result = parse_resume(resume)
    
    assert any("master" in edu.lower() for edu in result["education"])


def test_parse_resume_handles_missing_info():
    resume = "Some text without proper structure"
    result = parse_resume(resume)
    
    # Should not crash and return defaults
    assert result["full_name"] is not None
    assert result["email"] is None
    assert result["phone"] is None
    assert isinstance(result["skills"], list)
    assert isinstance(result["years_experience"], int)


def test_extract_skills_detects_technologies():
    text = "Experience with Python, Java, JavaScript, React, Node.js, PostgreSQL, MongoDB"
    skills = extract_skills(text)
    
    assert "Python" in skills
    assert "Java" in skills
    assert "Node.Js" in skills or "Node.js" in skills
    assert "Postgresql" in skills or "PostgreSQL" in skills


def test_extract_keywords_returns_relevant_terms():
    text = """
    Software engineer with extensive experience in machine learning,
    deep learning, natural language processing, and computer vision.
    Worked with TensorFlow, PyTorch, and scikit-learn frameworks.
    """
    keywords = extract_keywords(text)
    
    assert len(keywords) > 0
    assert isinstance(keywords, list)


def test_extract_keywords_empty_for_short_text():
    keywords = extract_keywords("Short text.")
    assert keywords == []