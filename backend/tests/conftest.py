"""
Pytest configuration and fixtures for backend tests.
"""

import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.main import app
from app.database.models import Candidate, JobDescription, AnalysisResult, Skill, CandidateSkill


# Disable sentence transformers for faster tests
os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    john.doe@example.com
    +1-555-123-4567
    
    Software Engineer with 5 years of experience in Python, JavaScript, React, 
    Node.js, FastAPI, PostgreSQL, Docker, and AWS.
    
    Education:
    Bachelor of Science in Computer Science
    University of Technology, 2018
    
    Experience:
    Senior Software Engineer at Tech Corp (2021-Present)
    - Developed microservices using Python and FastAPI
    - Built responsive frontends with React and TypeScript
    - Managed AWS infrastructure and CI/CD pipelines
    
    Software Engineer at StartupXYZ (2019-2021)
    - Created REST APIs using Node.js and Express
    - Implemented database schemas in PostgreSQL
    - Used Docker for containerization
    
    Skills:
    Python, JavaScript, TypeScript, React, Node.js, FastAPI, Django, 
    PostgreSQL, MySQL, MongoDB, Redis, Docker, Kubernetes, AWS, 
    Git, CI/CD, Unit Testing, Pytest
    """


@pytest.fixture
def sample_jd_text():
    """Sample job description text for testing."""
    return """
    Senior Software Engineer Position
    
    Requirements:
    - 3+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React and Node.js
    - Knowledge of PostgreSQL and Redis
    - Familiarity with Docker and AWS
    - Bachelor's degree in Computer Science or related field
    
    Preferred Skills:
    - Experience with FastAPI or Django
    - Knowledge of Kubernetes
    - CI/CD experience
    """


@pytest.fixture
def sample_candidate(db_session, sample_resume_text):
    """Create a sample candidate in the database."""
    candidate = Candidate(
        full_name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        resume_url="https://storage.example.com/resumes/john-doe.pdf",
        extracted_text=sample_resume_text,
        score=0,
        rank=None,
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


@pytest.fixture
def sample_job_description(db_session, sample_jd_text):
    """Create a sample job description in the database."""
    jd = JobDescription(
        title="Senior Software Engineer",
        content=sample_jd_text,
    )
    db_session.add(jd)
    db_session.commit()
    db_session.refresh(jd)
    return jd


@pytest.fixture
def sample_candidates_batch(db_session):
    """Create multiple sample candidates for batch testing."""
    candidates_data = [
        {
            "full_name": "Alice Smith",
            "email": "alice@example.com",
            "extracted_text": """
                Alice Smith
                alice@example.com
                5 years Python, React, AWS, Docker, PostgreSQL
                Bachelor Computer Science
            """,
        },
        {
            "full_name": "Bob Johnson",
            "email": "bob@example.com",
            "extracted_text": """
                Bob Johnson
                bob@example.com
                2 years JavaScript, Node.js, MongoDB
                Associate Degree
            """,
        },
        {
            "full_name": "Carol Williams",
            "email": "carol@example.com",
            "extracted_text": """
                Carol Williams
                carol@example.com
                8 years Python, Java, Kubernetes, GCP, MySQL
                Master Computer Science
            """,
        },
    ]
    
    candidates = []
    for data in candidates_data:
        candidate = Candidate(
            full_name=data["full_name"],
            email=data["email"],
            resume_url=f"https://storage.example.com/resumes/{data['full_name'].lower().replace(' ', '-')}.pdf",
            extracted_text=data["extracted_text"],
            score=0,
            rank=None,
        )
        db_session.add(candidate)
        candidates.append(candidate)
    
    db_session.commit()
    for c in candidates:
        db_session.refresh(c)
    
    return candidates