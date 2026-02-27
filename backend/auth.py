"""Authentication utilities for Streamlit app."""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_DB_PATH = Path("data/users.db")
PBKDF2_ITERATIONS = 120_000
VALID_ROLES = {"admin", "customer"}


def _resolve_db_path(db_path: str | Path | None = None) -> Path:
    if db_path is None:
        return DEFAULT_DB_PATH
    return Path(db_path)


def init_auth_db(db_path: str | Path | None = None) -> None:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = conn.execute("PRAGMA table_info(users)").fetchall()
        column_names = {str(col[1]) for col in columns}
        if "role" not in column_names:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'customer'")
            conn.execute("UPDATE users SET role='customer' WHERE role IS NULL OR role=''")
        conn.commit()


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return digest.hex()


def register_user(
    username: str,
    email: str,
    password: str,
    role: str = "customer",
    db_path: str | Path | None = None,
) -> Tuple[bool, str]:
    path = _resolve_db_path(db_path)
    username = username.strip()
    email = email.strip().lower()
    role = role.strip().lower()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if role not in VALID_ROLES:
        return False, "Role must be either admin or customer."

    salt = os.urandom(16)
    password_hash = _hash_password(password, salt)

    try:
        with sqlite3.connect(path) as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, salt.hex(), role),
            )
            conn.commit()
        return True, "Registration successful. Please login."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."


def login_user(
    username: str,
    password: str,
    db_path: str | Path | None = None,
) -> Tuple[bool, Dict[str, str] | str]:
    path = _resolve_db_path(db_path)
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."

    with sqlite3.connect(path) as conn:
        row = conn.execute(
            """
            SELECT username, password_hash, salt, role
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    if row is None:
        return False, "Invalid username or password."

    db_username, db_hash, db_salt, db_role = row
    candidate_hash = _hash_password(password, bytes.fromhex(db_salt))
    if not hmac.compare_digest(candidate_hash, db_hash):
        return False, "Invalid username or password."

    role = str(db_role).strip().lower() if db_role else "customer"
    if role not in VALID_ROLES:
        role = "customer"
    return True, {"username": db_username, "role": role}


def list_users(db_path: str | Path | None = None) -> List[Dict[str, object]]:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT id, username, email, role, created_at
            FROM users
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [
        {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]
