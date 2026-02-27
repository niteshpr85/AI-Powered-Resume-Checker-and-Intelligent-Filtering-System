"""Saved job description storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_DB_PATH = Path("data/jobs.db")


def _resolve_db_path(db_path: str | Path | None = None) -> Path:
    if db_path is None:
        return DEFAULT_DB_PATH
    return Path(db_path)


def init_job_db(db_path: str | Path | None = None) -> None:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL,
                title TEXT NOT NULL,
                jd_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(owner, title)
            )
            """
        )
        conn.commit()


def create_saved_job(
    owner: str,
    title: str,
    jd_text: str,
    db_path: str | Path | None = None,
) -> Tuple[bool, str]:
    owner = owner.strip()
    title = title.strip()
    jd_text = jd_text.strip()

    if not owner:
        return False, "Owner is required."
    if len(title) < 3:
        return False, "Job title must be at least 3 characters."
    if len(jd_text) < 30:
        return False, "JD text is too short to save."

    path = _resolve_db_path(db_path)
    try:
        with sqlite3.connect(path) as conn:
            conn.execute(
                """
                INSERT INTO saved_jobs (owner, title, jd_text)
                VALUES (?, ?, ?)
                """,
                (owner, title, jd_text),
            )
            conn.commit()
        return True, "Saved job created."
    except sqlite3.IntegrityError:
        return False, "This job title already exists for your account."


def list_saved_jobs(owner: str, db_path: str | Path | None = None) -> List[Dict[str, object]]:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT id, title, jd_text, created_at
            FROM saved_jobs
            WHERE owner = ?
            ORDER BY created_at DESC
            """,
            (owner,),
        ).fetchall()

    output: List[Dict[str, object]] = []
    for row in rows:
        output.append(
            {
                "id": row[0],
                "title": row[1],
                "jd_text": row[2],
                "created_at": row[3],
            }
        )
    return output


def list_all_saved_jobs(db_path: str | Path | None = None) -> List[Dict[str, object]]:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT id, owner, title, jd_text, created_at
            FROM saved_jobs
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [
        {
            "id": row[0],
            "owner": row[1],
            "title": row[2],
            "jd_text": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def delete_saved_job(owner: str, job_id: int, db_path: str | Path | None = None) -> Tuple[bool, str]:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM saved_jobs
            WHERE id = ? AND owner = ?
            """,
            (int(job_id), owner),
        )
        conn.commit()
    if cursor.rowcount == 0:
        return False, "Saved job not found."
    return True, "Saved job deleted."


def delete_saved_job_admin(job_id: int, db_path: str | Path | None = None) -> Tuple[bool, str]:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM saved_jobs
            WHERE id = ?
            """,
            (int(job_id),),
        )
        conn.commit()
    if cursor.rowcount == 0:
        return False, "Saved job not found."
    return True, "Saved job deleted."


def get_saved_job(owner: str, job_id: int, db_path: str | Path | None = None) -> Dict[str, object] | None:
    path = _resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        row = conn.execute(
            """
            SELECT id, title, jd_text, created_at
            FROM saved_jobs
            WHERE id = ? AND owner = ?
            """,
            (int(job_id), owner),
        ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "title": row[1], "jd_text": row[2], "created_at": row[3]}
