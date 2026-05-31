import re

from sklearn.feature_extraction.text import TfidfVectorizer

from app.ai.skills import SKILL_TERMS


def _contains_term(text: str, term: str) -> bool:
    lowered = text.lower()
    clean = re.escape(term.lower())
    if any(char in term for char in "+#./"):
        return term.lower() in lowered
    return bool(re.search(rf"(?<!\w){clean}(?!\w)", lowered))


def extract_skills(text: str) -> list[str]:
    matches = [skill for skill in SKILL_TERMS if _contains_term(text, skill)]
    return sorted({skill.title() for skill in matches})


def extract_keywords(text: str, limit: int = 25) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned.split()) < 4:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=limit)
    try:
        matrix = vectorizer.fit_transform([cleaned])
        scores = matrix.toarray()[0]
        terms = zip(vectorizer.get_feature_names_out(), scores, strict=False)
        return [term for term, _ in sorted(terms, key=lambda item: item[1], reverse=True)]
    except ValueError:
        return []


def overlap_score(required: list[str], available_text: str) -> tuple[list[str], list[str], float]:
    matched = [term for term in required if _contains_term(available_text, term)]
    missing = [term for term in required if term not in matched]
    score = len(matched) / len(required) if required else 1.0
    return matched, missing, score

