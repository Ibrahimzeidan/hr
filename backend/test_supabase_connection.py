#!/usr/bin/env python3
"""
Test script to verify Supabase PostgreSQL connection and CRUD operations.
Run this after starting the backend to verify database connectivity.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine, check_db_connection, Base
from app.database.models import Candidate, JobDescription, AnalysisResult, Skill, CandidateSkill
from app.core.config import get_settings
from sqlalchemy.orm import Session
from sqlalchemy import text


def test_connection():
    """Test basic database connection."""
    print("\n=== Testing Database Connection ===")
    settings = get_settings()
    print(f"DATABASE_URL: {settings.database_url[:50]}...")
    
    result = check_db_connection()
    print(f"Connection status: {result}")
    
    if result["connected"]:
        print("✓ Database connection successful!")
    else:
        print(f"✗ Database connection failed: {result['error']}")
        return False
    
    return True


def test_migrations():
    """Test that all tables exist."""
    print("\n=== Testing Database Tables ===")
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('candidates', 'job_descriptions', 'analysis_results', 'skills', 'candidate_skills')
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Found tables: {tables}")
            
            expected_tables = ['analysis_results', 'candidate_skills', 'candidates', 'job_descriptions', 'skills']
            if set(tables) == set(expected_tables):
                print("✓ All expected tables exist!")
                return True
            else:
                missing = set(expected_tables) - set(tables)
                if missing:
                    print(f"✗ Missing tables: {missing}")
                    print("  Run 'alembic upgrade head' to create tables")
                    return False
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        return False
    
    return True


def test_crud_operations():
    """Test basic CRUD operations."""
    print("\n=== Testing CRUD Operations ===")
    
    try:
        # Create a test session
        from app.database.session import SessionLocal
        db = SessionLocal()
        
        # CREATE - Create a test job description
        print("Testing CREATE...")
        jd = JobDescription(content="Test job description for testing purposes")
        db.add(jd)
        db.commit()
        db.refresh(jd)
        print(f"  Created job description with ID: {jd.id}")
        
        # CREATE - Create a test candidate
        candidate = Candidate(
            full_name="Test Candidate",
            email="test@example.com",
            phone="+1234567890",
            resume_url="https://example.com/resume.pdf",
            extracted_text="Test candidate with Python and SQL skills"
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        print(f"  Created candidate with ID: {candidate.id}")
        
        # READ - Read the candidate back
        print("Testing READ...")
        retrieved = db.query(Candidate).filter(Candidate.id == candidate.id).first()
        assert retrieved is not None, "Candidate not found"
        assert retrieved.full_name == "Test Candidate", "Candidate name mismatch"
        print(f"  Read candidate: {retrieved.full_name}")
        
        # UPDATE - Update the candidate
        print("Testing UPDATE...")
        retrieved.score = 85.5
        db.commit()
        db.refresh(retrieved)
        assert retrieved.score == 85.5, "Score not updated"
        print(f"  Updated candidate score: {retrieved.score}")
        
        # DELETE - Clean up test data
        print("Testing DELETE...")
        db.delete(retrieved)
        db.delete(jd)
        db.commit()
        print("  Deleted test data")
        
        db.close()
        print("✓ All CRUD operations successful!")
        return True
        
    except Exception as e:
        print(f"✗ CRUD test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Supabase PostgreSQL Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_connection()))
    
    # Test 2: Migrations/Tables
    if results[0][1]:
        results.append(("Migrations", test_migrations()))
    
    # Test 3: CRUD Operations
    if len(results) > 1 and results[1][1]:
        results.append(("CRUD Operations", test_crud_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Supabase integration is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())