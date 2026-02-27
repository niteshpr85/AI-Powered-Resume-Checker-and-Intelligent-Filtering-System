from backend.scoring_engine import score_candidate


def test_score_candidate_returns_expected_keys():
    candidate = {
        "skills": ["Python", "SQL"],
        "experience_years": 3,
        "education": "bachelor",
        "raw_text": "Built APIs using Python and SQL. Improved performance by 20%.",
    }
    jd_data = {
        "raw_jd": "Need Python SQL developer with 2 years experience and bachelor degree.",
        "required_skills": ["Python", "SQL", "Docker"],
        "required_experience": 2,
        "required_education": "bachelor",
    }
    result = score_candidate(candidate, jd_data)
    for key in [
        "ats_score",
        "skill_match",
        "semantic_similarity",
        "experience_match",
        "education_match",
        "quality_score",
        "matched_skills",
        "missing_skills",
    ]:
        assert key in result

