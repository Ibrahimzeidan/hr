import re
from functools import lru_cache

import spacy

from app.ai.keyword_matcher import extract_keywords, extract_skills
from app.ai.skills import DEGREE_TERMS


@lru_cache(maxsize=1)
def _nlp():
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return spacy.blank("en")


def _section(text: str, names: list[str]) -> list[str]:
    pattern = "|".join(re.escape(name) for name in names)
    match = re.search(rf"(?is)({pattern})\s*:?\s*(.*?)(\n[A-Z][A-Za-z ]{{2,}}:?\n|$)", text)
    return [line.strip(" -•\t") for line in match.group(2).splitlines() if line.strip()] if match else []


def _name(text: str, email: str | None) -> str:
    doc = _nlp()(text[:1200])
    for ent in getattr(doc, "ents", []):
        if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
            return ent.text.strip()
    for line in [item.strip() for item in text.splitlines()[:12] if item.strip()]:
        if email and email in line:
            continue
        if re.search(r"\d|resume|curriculum|phone|email|linkedin", line, re.I):
            continue
        if 1 < len(line.split()) <= 4:
            return line
    return "Unknown Candidate"


def parse_resume(text: str) -> dict:
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone_match = re.search(r"(\+?\d[\d\s().-]{8,}\d)", text)
    years = [int(item) for item in re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)", text, re.I)]
    education = _section(text, ["education", "academic background"])
    certs = _section(text, ["certifications", "licenses"])
    projects = _section(text, ["projects", "portfolio"])
    degree_hits = [term.title() for term in DEGREE_TERMS if term in text.lower()]
    return {
        "full_name": _name(text, email_match.group(0) if email_match else None),
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(1).strip() if phone_match else None,
        "skills": extract_skills(text),
        "education": education or degree_hits,
        "experience": _section(text, ["experience", "work experience", "employment"]),
        "years_experience": max(years) if years else 0,
        "certifications": certs,
        "projects": projects,
        "keywords": extract_keywords(text),
    }

