from backend.skill_extractor import extract_skills


def test_extract_skills_handles_special_character_skills():
    text = "Built backend APIs in Node.js and C++. Managed CI/CD pipelines on AWS."
    skills = extract_skills(text)
    assert "Node.js" in skills
    assert "C++" in skills
    assert "CI/CD" in skills
    assert "AWS" in skills

