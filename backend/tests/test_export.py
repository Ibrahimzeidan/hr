"""
Tests for export functionality (CSV and Excel).
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from sqlalchemy.orm import sessionmaker

from app.services.export_service import (
    candidates_dataframe,
    csv_bytes,
    excel_bytes,
    _row_to_dict,
)
from app.database.models import Candidate, AnalysisResult


def test_csv_export_generates_valid_csv(test_engine):
    """Test that CSV export generates valid CSV content."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Add a candidate
        candidate = Candidate(
            full_name="Export Test",
            email="export@test.com",
            phone="123-456-7890",
            resume_url="https://example.com/resume.pdf",
            extracted_text="Test resume content",
            score=85.5,
            rank=1,
        )
        db.add(candidate)
        db.commit()
        
        # Export to CSV
        csv_data = csv_bytes(db)
        
        # Verify CSV content
        assert isinstance(csv_data, bytes)
        csv_str = csv_data.decode("utf-8")
        assert "Export Test" in csv_str
        assert "export@test.com" in csv_str
        assert "85.5" in csv_str
        
    finally:
        db.rollback()
        db.close()


def test_excel_export_generates_valid_excel(test_engine):
    """Test that Excel export generates valid Excel content."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Add a candidate
        candidate = Candidate(
            full_name="Excel Test",
            email="excel@test.com",
            resume_url="https://example.com/resume.pdf",
            extracted_text="Test resume content",
            score=75.0,
            rank=2,
        )
        db.add(candidate)
        db.commit()
        
        # Export to Excel
        excel_data = excel_bytes(db)
        
        # Verify Excel content (should start with ZIP header)
        assert isinstance(excel_data, bytes)
        assert len(excel_data) > 0
        # Excel files start with PK (ZIP format)
        assert excel_data[:2] == b"PK"
        
    finally:
        db.rollback()
        db.close()


def test_candidates_dataframe_includes_all_fields(test_engine):
    """Test that dataframe includes all candidate fields."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Add candidate with analysis
        candidate = Candidate(
            full_name="DataFrame Test",
            email="df@test.com",
            resume_url="https://example.com/resume.pdf",
            extracted_text="Test content",
            score=90.0,
            rank=1,
        )
        db.add(candidate)
        db.commit()
        
        analysis = AnalysisResult(
            candidate_id=candidate.id,
            matching_skills=["Python", "React"],
            missing_skills=["AWS"],
            semantic_similarity=85.0,
            keyword_score=75.0,
            explanation="Strong candidate",
            candidate_summary="Experienced developer",
            hiring_recommendation="Hire",
            confidence_score=80.0,
            strengths=["Good skills"],
            weaknesses=["Missing cloud"],
            recommendations=["Learn AWS"],
        )
        db.add(analysis)
        db.commit()
        
        # Get dataframe
        df = candidates_dataframe(db)
        
        # Verify columns exist
        assert "Candidate Name" in df.columns
        assert "Email" in df.columns
        assert "Score" in df.columns
        assert "Matching Skills" in df.columns
        assert "Missing Skills" in df.columns
        assert "Hiring Recommendation" in df.columns
        assert "Confidence Score" in df.columns
        
        # Verify data
        assert len(df) == 1
        assert df.iloc[0]["Candidate Name"] == "DataFrame Test"
        assert df.iloc[0]["Score"] == 90.0
        
    finally:
        db.rollback()
        db.close()


def test_row_to_dict_includes_gemini_fields():
    """Test that row_to_dict includes all Gemini-enhanced fields."""
    # Create a mock candidate object
    class MockAnalysis:
        def __init__(self):
            self.matching_skills = ["Python"]
            self.missing_skills = ["Java"]
            self.semantic_similarity = 80.0
            self.keyword_score = 70.0
            self.explanation = "Test explanation"
            self.candidate_summary = "Test summary"
            self.hiring_recommendation = "Hire"
            self.confidence_score = 75.0
            self.strengths = ["Strong Python"]
            self.weaknesses = ["No Java"]
            self.recommendations = ["Learn Java"]
            self.ai_provider = "local_fallback"
            self.ai_model = None
    
    class MockCandidate:
        def __init__(self):
            self.rank = 1
            self.full_name = "Test Candidate"
            self.email = "test@example.com"
            self.phone = "123-456"
            self.resume_url = "https://example.com/resume.pdf"
            self.score = 85.0
            self.created_at = None
            self.analysis = MockAnalysis()
    
    candidate = MockCandidate()
    result = _row_to_dict(candidate)
    
    # Verify all fields are present
    assert result["Rank"] == 1
    assert result["Candidate Name"] == "Test Candidate"
    assert result["Email"] == "test@example.com"
    assert result["Score"] == 85.0
    assert result["Matching Skills"] == "Python"
    assert result["Missing Skills"] == "Java"
    assert result["Candidate Summary"] == "Test summary"
    assert result["Hiring Recommendation"] == "Hire"
    assert result["Confidence Score"] == 75.0
    assert result["Strengths"] == "Strong Python"
    assert result["Weaknesses"] == "No Java"
    assert result["Recommendations"] == "Learn Java"
    assert result["AI Provider"] == "local_fallback"


def test_export_handles_missing_analysis(test_engine):
    """Test that export handles candidates without analysis."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Add candidate without analysis
        candidate = Candidate(
            full_name="No Analysis",
            email="noanalysis@test.com",
            resume_url="https://example.com/resume.pdf",
            extracted_text="Test content",
            score=0,
            rank=None,
        )
        db.add(candidate)
        db.commit()
        
        # Should not raise exception
        df = candidates_dataframe(db)
        assert len(df) == 1
        assert df.iloc[0]["Candidate Name"] == "No Analysis"
        
    finally:
        db.rollback()
        db.close()


def test_export_empty_database(test_engine):
    """Test that export handles empty database."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Should not raise exception
        df = candidates_dataframe(db)
        assert len(df) == 0
        
        csv_data = csv_bytes(db)
        assert isinstance(csv_data, bytes)
        
        excel_data = excel_bytes(db)
        assert isinstance(excel_data, bytes)
        
    finally:
        db.rollback()
        db.close()