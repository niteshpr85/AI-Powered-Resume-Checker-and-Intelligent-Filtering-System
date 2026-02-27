from backend.filter_engine import filter_candidates


def test_filter_candidates_marks_rejected_when_below_threshold():
    rows = [
        {"name": "A", "ats_score": 80, "experience_years": 3, "skills": ["Python"]},
        {"name": "B", "ats_score": 50, "experience_years": 1, "skills": ["SQL"]},
    ]
    result = filter_candidates(rows, min_score=70, min_experience=2)
    assert result[0]["status"] == "Shortlisted"
    assert result[1]["status"] == "Rejected"

