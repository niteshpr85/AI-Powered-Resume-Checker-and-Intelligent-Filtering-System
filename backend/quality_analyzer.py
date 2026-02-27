"""Resume quality analysis."""

from __future__ import annotations

import re
from typing import Dict, List

from utils.constants import ACTION_VERBS
from utils.helpers import clamp


def _count_action_verbs(text: str) -> int:
    lower = text.lower()
    return sum(1 for verb in ACTION_VERBS if re.search(r"\b" + re.escape(verb) + r"\b", lower))


def analyze_resume_quality(text: str) -> Dict[str, object]:
    content = text.strip()
    if not content:
        return {"quality_score": 0.0, "quality_feedback": ["Resume text is empty or unreadable."]}

    feedback: List[str] = []
    score = 0.0

    length = len(content)
    if length >= 600:
        score += 20
    elif length >= 300:
        score += 14
        feedback.append("Add more details for projects and quantified achievements.")
    else:
        score += 8
        feedback.append("Resume appears too short; include relevant work, skills, and impact.")

    metric_hits = len(re.findall(r"\b\d+%|\b\d+\b", content))
    if metric_hits >= 8:
        score += 25
    elif metric_hits >= 4:
        score += 18
        feedback.append("Add more measurable outcomes (for example percentages and counts).")
    else:
        score += 10
        feedback.append("Use quantified achievements to strengthen impact.")

    action_hits = _count_action_verbs(content)
    if action_hits >= 8:
        score += 20
    elif action_hits >= 4:
        score += 14
    else:
        score += 8
        feedback.append("Use stronger action verbs (built, optimized, delivered, reduced).")

    sections = ["experience", "skills", "education", "project"]
    section_hits = sum(1 for item in sections if item in content.lower())
    score += section_hits * 8
    if section_hits < 3:
        feedback.append("Include clear sections for Experience, Skills, Education, and Projects.")

    if not feedback:
        feedback.append("Resume quality is strong. Keep this structure and clarity.")

    return {"quality_score": round(clamp(score), 2), "quality_feedback": feedback}

