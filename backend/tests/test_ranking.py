"""
Tests for candidate ranking functionality.
"""

import os

os.environ["DISABLE_SENTENCE_TRANSFORMERS"] = "1"

from sqlalchemy.orm import Session

from app.database.models import Candidate
from app.services.ranking_service import refresh_ranks


def test_refresh_ranks_orders_by_score_desc(test_engine):
    """Test that ranks are assigned in descending score order."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Create candidates with different scores
        candidates = [
            Candidate(full_name="Low Score", email="low@test.com", score=30, resume_url="url1", extracted_text="text1"),
            Candidate(full_name="High Score", email="high@test.com", score=90, resume_url="url2", extracted_text="text2"),
            Candidate(full_name="Mid Score", email="mid@test.com", score=60, resume_url="url3", extracted_text="text3"),
        ]
        
        for c in candidates:
            db.add(c)
        db.commit()
        
        # Refresh ranks
        refresh_ranks(db)
        
        # Verify ranking order
        ranked = db.query(Candidate).order_by(Candidate.rank).all()
        assert ranked[0].full_name == "High Score"
        assert ranked[0].rank == 1
        assert ranked[1].full_name == "Mid Score"
        assert ranked[1].rank == 2
        assert ranked[2].full_name == "Low Score"
        assert ranked[2].rank == 3
        
    finally:
        db.rollback()
        db.close()


def test_refresh_ranks_handles_tied_scores(test_engine):
    """Test that tied scores are handled consistently."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Create candidates with same score
        candidates = [
            Candidate(full_name="Tied A", email="ta@test.com", score=70, resume_url="url1", extracted_text="text1"),
            Candidate(full_name="Tied B", email="tb@test.com", score=70, resume_url="url2", extracted_text="text2"),
        ]
        
        for c in candidates:
            db.add(c)
        db.commit()
        
        # Refresh ranks
        refresh_ranks(db)
        
        # Both should have ranks assigned (may differ due to creation order)
        ranked = db.query(Candidate).order_by(Candidate.rank).all()
        assert len(ranked) == 2
        assert all(c.rank is not None for c in ranked)
        
    finally:
        db.rollback()
        db.close()


def test_refresh_ranks_updates_existing_ranks(test_engine):
    """Test that ranks are updated when scores change."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Create and rank candidates
        c1 = Candidate(full_name="First", email="f@test.com", score=50, resume_url="url1", extracted_text="text1")
        c2 = Candidate(full_name="Second", email="s@test.com", score=100, resume_url="url2", extracted_text="text2")
        
        db.add(c1)
        db.add(c2)
        db.commit()
        
        refresh_ranks(db)
        
        # Verify initial ranking
        assert db.get(Candidate, c1.id).rank == 2
        assert db.get(Candidate, c2.id).rank == 1
        
        # Update score
        c1.score = 150
        db.commit()
        
        # Re-rank
        refresh_ranks(db)
        
        # Verify updated ranking
        assert db.get(Candidate, c1.id).rank == 1
        assert db.get(Candidate, c2.id).rank == 2
        
    finally:
        db.rollback()
        db.close()


def test_refresh_ranks_empty_database(test_engine):
    """Test that refresh_ranks handles empty database gracefully."""
    Session = sessionmaker(bind=test_engine)
    db = Session()
    
    try:
        # Should not raise any exception
        refresh_ranks(db)
        
    finally:
        db.rollback()
        db.close()