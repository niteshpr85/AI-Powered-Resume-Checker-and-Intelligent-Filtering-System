"""Skill extraction and matching logic."""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from utils.constants import SKILL_ALIASES, SKILL_CATALOG
from utils.helpers import clamp, safe_divide


def _normalize_for_matching(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[\r\n\t/|,;:()\[\]{}]+", " ", normalized)
    normalized = re.sub(r"\s{2,}", " ", normalized)
    return normalized.strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    if not phrase:
        return False

    # Handle terms like C++, Node.js, CI/CD with non-word characters.
    pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    if re.search(pattern, text):
        return True

    # Fallback: punctuation-normalized matching.
    norm_text = _normalize_for_matching(text)
    norm_phrase = _normalize_for_matching(phrase)
    pattern_norm = r"(?<![a-z0-9])" + re.escape(norm_phrase) + r"(?![a-z0-9])"
    return bool(re.search(pattern_norm, norm_text))


def extract_skills(text: str) -> List[str]:
    lower_text = text.lower()
    found = set()

    for skill in SKILL_CATALOG:
        if _contains_phrase(lower_text, skill.lower()):
            found.add(skill)
            continue

        aliases = SKILL_ALIASES.get(skill, [])
        for alias in aliases:
            if _contains_phrase(lower_text, alias.lower()):
                found.add(skill)
                break

    return sorted(found)


def compute_skill_match(
    candidate_skills: Sequence[str],
    required_skills: Sequence[str],
) -> Dict[str, object]:
    candidate_set = {skill.lower() for skill in candidate_skills}
    required_set = {skill.lower() for skill in required_skills if skill}

    if not required_set:
        return {
            "skill_match": 100.0,
            "matched_skills": sorted(candidate_skills),
            "missing_skills": [],
        }

    matched = sorted(skill for skill in required_set if skill in candidate_set)
    missing = sorted(skill for skill in required_set if skill not in candidate_set)
    score = clamp(safe_divide(len(matched), len(required_set)) * 100.0)

    return {
        "skill_match": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }
