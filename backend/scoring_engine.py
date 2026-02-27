"""ATS scoring engine."""

from __future__ import annotations

from typing import Dict

from backend.quality_analyzer import analyze_resume_quality
from backend.similarity_engine import compute_semantic_similarity
from backend.skill_extractor import compute_skill_match
from utils.constants import EDUCATION_RANK
from utils.helpers import clamp, normalize_weights


def _experience_match(candidate_years: int, required_years: int) -> float:
    if required_years <= 0:
        if candidate_years >= 1:
            return 100.0
        return 70.0
    if candidate_years >= required_years:
        return 100.0
    return clamp((candidate_years / required_years) * 100.0)


def _education_match(candidate_education: str, required_education: str) -> float:
    candidate_rank = EDUCATION_RANK.get(candidate_education.lower(), 1)
    required_rank = EDUCATION_RANK.get(required_education.lower(), 1)

    if candidate_rank >= required_rank:
        return 100.0
    if required_rank <= 1:
        return 100.0
    return clamp((candidate_rank / required_rank) * 100.0)


def score_candidate(candidate: Dict[str, object], jd_data: Dict[str, object], weights: Dict[str, float] | None = None) -> Dict[str, object]:
    normalized_weights = normalize_weights(weights)

    skill_result = compute_skill_match(
        candidate_skills=candidate.get("skills", []),
        required_skills=jd_data.get("required_skills", []),
    )
    semantic_score = compute_semantic_similarity(
        jd_text=str(jd_data.get("raw_jd", "")),
        resume_text=str(candidate.get("raw_text", "")),
    )
    experience_score = _experience_match(
        candidate_years=int(candidate.get("experience_years", 0)),
        required_years=int(jd_data.get("required_experience", 0)),
    )
    education_score = _education_match(
        candidate_education=str(candidate.get("education", "high school")),
        required_education=str(jd_data.get("required_education", "high school")),
    )
    quality_result = analyze_resume_quality(str(candidate.get("raw_text", "")))
    quality_score = float(quality_result["quality_score"])

    final_score = (
        skill_result["skill_match"] * normalized_weights.get("skill", 0.0)
        + semantic_score * normalized_weights.get("semantic", 0.0)
        + experience_score * normalized_weights.get("experience", 0.0)
        + education_score * normalized_weights.get("education", 0.0)
        + quality_score * normalized_weights.get("quality", 0.0)
    )

    return {
        "ats_score": round(clamp(final_score), 2),
        "skill_match": round(float(skill_result["skill_match"]), 2),
        "semantic_similarity": round(semantic_score, 2),
        "experience_match": round(experience_score, 2),
        "education_match": round(education_score, 2),
        "quality_score": round(quality_score, 2),
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "quality_feedback": quality_result["quality_feedback"],
    }

