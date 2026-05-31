import re

from app.ai.keyword_matcher import extract_keywords, extract_skills
from app.ai.skills import DEGREE_TERMS


def parse_job_description(text: str) -> dict:
    years = [int(item) for item in re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)", text, re.I)]
    lowered = text.lower()
    return {
        "text": text,
        "required_skills": extract_skills(text),
        "keywords": extract_keywords(text),
        "education_terms": [term for term in DEGREE_TERMS if term in lowered],
        "min_years": max(years) if years else 0,
    }

