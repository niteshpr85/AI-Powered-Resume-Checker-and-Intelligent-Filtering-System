"""Decision explainability for recruiters."""

from __future__ import annotations

import math
from typing import Dict


def estimate_selection_probability(ats_score: float) -> float:
    # Smooth curve centered around 65 as decision pivot.
    probability = 1 / (1 + math.exp(-(ats_score - 65.0) / 10.0))
    return round(probability * 100.0, 2)


def explain_decision(candidate_row: Dict[str, object]) -> Dict[str, object]:
    status = str(candidate_row.get("status", "Rejected"))
    score = float(candidate_row.get("ats_score", 0.0))
    missing_skills = candidate_row.get("missing_skills", [])
    filter_reasons = candidate_row.get("filter_reasons", [])

    positives = []
    gaps = []

    if score >= 75:
        positives.append("Strong overall ATS score.")
    if float(candidate_row.get("skill_match", 0)) >= 70:
        positives.append("Good alignment with required skills.")
    if float(candidate_row.get("semantic_similarity", 0)) >= 60:
        positives.append("Resume content is contextually relevant to the JD.")

    if missing_skills:
        gaps.append(f"Missing skills: {', '.join(missing_skills)}.")
    if float(candidate_row.get("experience_match", 0)) < 60:
        gaps.append("Experience alignment is low.")
    if float(candidate_row.get("quality_score", 0)) < 55:
        gaps.append("Resume quality can be improved.")

    if filter_reasons:
        gaps.extend(filter_reasons)

    if not positives:
        positives.append("No major strengths detected by current thresholds.")
    if not gaps:
        gaps.append("No critical gaps found for current filter settings.")

    explanation = (
        f"Status: {status}\n"
        f"Why selected: {' '.join(positives)}\n"
        f"Gaps: {' '.join(gaps)}"
    )

    return {
        "selection_probability": estimate_selection_probability(score),
        "explanation": explanation,
    }

