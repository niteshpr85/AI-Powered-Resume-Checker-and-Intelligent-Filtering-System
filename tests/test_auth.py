from backend.auth import init_auth_db, login_user, register_user


def test_register_and_login_success(tmp_path):
    db_path = tmp_path / "users.db"
    init_auth_db(db_path=db_path)

    ok, _ = register_user("tester1", "tester1@example.com", "secret123", db_path=db_path)
    assert ok

    ok, payload = login_user("tester1", "secret123", db_path=db_path)
    assert ok
    assert isinstance(payload, dict)
    assert payload["username"] == "tester1"
    assert payload["role"] == "customer"


def test_register_duplicate_user_fails(tmp_path):
    db_path = tmp_path / "users.db"
    init_auth_db(db_path=db_path)

    ok1, _ = register_user("tester2", "tester2@example.com", "secret123", db_path=db_path)
    ok2, _ = register_user("tester2", "tester3@example.com", "secret123", db_path=db_path)
    assert ok1
    assert not ok2


def test_login_wrong_password_fails(tmp_path):
    db_path = tmp_path / "users.db"
    init_auth_db(db_path=db_path)
    register_user("tester3", "tester4@example.com", "secret123", db_path=db_path)

    ok, _ = login_user("tester3", "wrongpass", db_path=db_path)
    assert not ok


def test_register_admin_role_and_login(tmp_path):
    db_path = tmp_path / "users.db"
    init_auth_db(db_path=db_path)

    ok, _ = register_user("admin1", "admin1@example.com", "secret123", role="admin", db_path=db_path)
    assert ok

    ok, payload = login_user("admin1", "secret123", db_path=db_path)
    assert ok
    assert isinstance(payload, dict)
    assert payload["role"] == "admin"
