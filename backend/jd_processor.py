"""Job description processing logic."""

from __future__ import annotations

import re
from typing import Dict

from backend.skill_extractor import extract_skills
from utils.constants import EDUCATION_KEYWORDS, EDUCATION_RANK
from utils.text_cleaner import clean_text


def _extract_required_experience(text: str) -> int:
    patterns = [
        r"(\d{1,2})\+?\s+years?\s+of\s+experience",
        r"minimum\s+(\d{1,2})\+?\s+years?",
        r"at\s+least\s+(\d{1,2})\s+years?",
    ]
    lower = text.lower()
    matches = []
    for pattern in patterns:
        matches.extend(int(value) for value in re.findall(pattern, lower))
    return max(matches) if matches else 0


def _extract_required_education(text: str) -> str:
    lower = text.lower()
    best_level = "high school"
    best_rank = 1
    for level, terms in EDUCATION_KEYWORDS.items():
        for term in terms:
            if term in lower and EDUCATION_RANK[level] > best_rank:
                best_level = level
                best_rank = EDUCATION_RANK[level]
    return best_level


def process_jd(jd_text: str) -> Dict[str, object]:
    cleaned = clean_text(jd_text)
    return {
        "raw_jd": cleaned,
        "required_skills": extract_skills(cleaned),
        "required_experience": _extract_required_experience(cleaned),
        "required_education": _extract_required_education(cleaned),
    }

