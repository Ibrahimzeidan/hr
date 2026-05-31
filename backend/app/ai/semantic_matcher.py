from functools import lru_cache
from os import getenv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@lru_cache(maxsize=1)
def _model():
    if getenv("DISABLE_SENTENCE_TRANSFORMERS") == "1":
        return None
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        return None


def semantic_similarity(source: str, target: str) -> float:
    if not source.strip() or not target.strip():
        return 0.0
    model = _model()
    if model is not None:
        vectors = model.encode([source, target])
        return float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([source, target])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])
