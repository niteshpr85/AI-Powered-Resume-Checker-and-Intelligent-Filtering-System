"""Candidate filtering logic."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence


def _has_required_skills(candidate_skills: Sequence[str], required_skills: Sequence[str]) -> bool:
    if not required_skills:
        return True
    candidate_set = {skill.lower() for skill in candidate_skills}
    return all(skill.lower() in candidate_set for skill in required_skills)


def filter_candidates(
    rows: Iterable[Dict[str, object]],
    min_score: float = 70.0,
    min_experience: int = 0,
    required_skills: Sequence[str] | None = None,
) -> List[Dict[str, object]]:
    required_skills = required_skills or []
    filtered = []
    for row in rows:
        reasons = []
        status = "Shortlisted"

        if float(row.get("ats_score", 0)) < min_score:
            status = "Rejected"
            reasons.append(f"ATS below threshold ({min_score}).")
        if int(row.get("experience_years", 0)) < min_experience:
            status = "Rejected"
            reasons.append(f"Experience below required minimum ({min_experience} years).")
        if not _has_required_skills(row.get("skills", []), required_skills):
            status = "Rejected"
            reasons.append("Missing recruiter-selected required skills.")

        enriched = dict(row)
        enriched["status"] = status
        enriched["filter_reasons"] = reasons
        filtered.append(enriched)
    return filtered

