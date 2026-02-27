from backend.job_store import (
    create_saved_job,
    delete_saved_job,
    delete_saved_job_admin,
    get_saved_job,
    init_job_db,
    list_all_saved_jobs,
    list_saved_jobs,
)


def test_create_and_list_saved_jobs(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_job_db(db_path=db_path)

    ok, _ = create_saved_job(
        owner="tester1",
        title="Backend Engineer",
        jd_text="Need Python, SQL, and FastAPI with 2 years experience.",
        db_path=db_path,
    )
    assert ok

    jobs = list_saved_jobs(owner="tester1", db_path=db_path)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Backend Engineer"


def test_saved_job_unique_per_owner(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_job_db(db_path=db_path)

    ok1, _ = create_saved_job("tester1", "Data Analyst", "Need SQL and Python skills for analytics role.", db_path=db_path)
    ok2, _ = create_saved_job("tester1", "Data Analyst", "Another JD text with enough characters.", db_path=db_path)
    ok3, _ = create_saved_job("tester2", "Data Analyst", "Another JD text with enough characters.", db_path=db_path)
    assert ok1
    assert not ok2
    assert ok3


def test_get_and_delete_saved_job(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_job_db(db_path=db_path)
    create_saved_job("tester1", "ML Engineer", "Need ML, Python, and deployment experience.", db_path=db_path)
    jobs = list_saved_jobs("tester1", db_path=db_path)
    job_id = int(jobs[0]["id"])

    job = get_saved_job("tester1", job_id, db_path=db_path)
    assert job is not None
    assert job["title"] == "ML Engineer"

    ok, _ = delete_saved_job("tester1", job_id, db_path=db_path)
    assert ok
    jobs_after = list_saved_jobs("tester1", db_path=db_path)
    assert len(jobs_after) == 0


def test_list_all_and_admin_delete_saved_job(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_job_db(db_path=db_path)
    create_saved_job("tester1", "Role One", "Need Python and APIs for backend development role.", db_path=db_path)
    create_saved_job("tester2", "Role Two", "Need SQL and dashboard development experience here.", db_path=db_path)

    all_jobs = list_all_saved_jobs(db_path=db_path)
    assert len(all_jobs) == 2
    target_id = int(all_jobs[0]["id"])

    ok, _ = delete_saved_job_admin(target_id, db_path=db_path)
    assert ok
    remaining_jobs = list_all_saved_jobs(db_path=db_path)
    assert len(remaining_jobs) == 1
