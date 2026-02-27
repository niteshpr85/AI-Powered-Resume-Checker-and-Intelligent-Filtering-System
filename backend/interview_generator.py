"""Generate interview questions from candidate profile."""

from __future__ import annotations

from typing import Dict, List


def generate_interview_questions(candidate: Dict[str, object], jd_data: Dict[str, object], max_questions: int = 6) -> List[str]:
    questions: List[str] = []

    matched_skills = candidate.get("matched_skills", [])[:3]
    missing_skills = candidate.get("missing_skills", [])[:2]

    for skill in matched_skills:
        questions.append(f"Can you explain a real project where you used {skill}?")

    for skill in missing_skills:
        questions.append(f"This role requires {skill}. How would you ramp up quickly in this area?")

    experience_years = int(candidate.get("experience_years", 0))
    questions.append(
        f"You have around {experience_years} years of experience. Which project best reflects your ownership and impact?"
    )

    questions.append("Describe a challenge you faced in a recent project and how you resolved it.")
    questions.append("How do you prioritize quality, deadlines, and collaboration in team delivery?")

    unique: List[str] = []
    for question in questions:
        if question not in unique:
            unique.append(question)
    return unique[:max_questions]

