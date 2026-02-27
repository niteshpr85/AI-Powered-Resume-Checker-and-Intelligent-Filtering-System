"""Semantic similarity engine."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.helpers import clamp


def compute_semantic_similarity(jd_text: str, resume_text: str) -> float:
    if not jd_text.strip() or not resume_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform([jd_text, resume_text])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100.0
    return round(clamp(float(score)), 2)

