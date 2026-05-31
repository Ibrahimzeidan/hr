from app.ai.jd_parser import parse_job_description
from app.ai.keyword_matcher import overlap_score
from app.ai.resume_parser import parse_resume
from app.ai.semantic_matcher import semantic_similarity


def score_resume(resume_text: str, jd_text: str) -> dict:
    resume = parse_resume(resume_text)
    jd = parse_job_description(jd_text)
    matched, missing, exact_skill_score = overlap_score(jd["required_skills"], resume_text)
    semantic = max(0.0, min(1.0, semantic_similarity(resume_text, jd_text)))
    keyword_matched, _, keyword_score = overlap_score(jd["keywords"], resume_text)
    skill_score = (exact_skill_score * 0.75) + (semantic * 0.25)
    experience_score = _experience_score(resume["years_experience"], jd["min_years"], semantic)
    education_score = _education_score(resume["education"], jd["education_terms"])
    total = (skill_score * 50) + (experience_score * 25) + (education_score * 15) + (keyword_score * 10)
    return {
        "score": round(min(total, 100), 2),
        "matching_skills": [item.title() for item in matched],
        "missing_skills": [item.title() for item in missing],
        "semantic_similarity": round(semantic * 100, 2),
        "keyword_score": round(keyword_score * 100, 2),
        "explanation": _explain(total, matched, missing, keyword_matched),
    }


def _experience_score(candidate_years: int, min_years: int, semantic: float) -> float:
    if not min_years:
        return 0.75 + (semantic * 0.25)
    return min(candidate_years / min_years, 1.0) * 0.8 + semantic * 0.2


def _education_score(education: list[str], required_terms: list[str]) -> float:
    if not required_terms:
        return 1.0
    haystack = " ".join(education).lower()
    return sum(1 for term in required_terms if term in haystack) / len(required_terms)


def _explain(total: float, matched: list[str], missing: list[str], keywords: list[str]) -> str:
    if total >= 80:
        base = "Strong alignment across required skills and role context."
    elif total >= 60:
        base = "Good fit with a few gaps to review during screening."
    else:
        base = "Partial alignment; several requirements need closer review."
    detail = f"Matched {len(matched)} skills and {len(keywords)} JD keywords."
    return f"{base} {detail} Missing skills: {', '.join(missing) if missing else 'none'}."

