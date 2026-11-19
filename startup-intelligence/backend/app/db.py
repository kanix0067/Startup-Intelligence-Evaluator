"""
Lightweight persistence layer.

NOTE ON SCOPE:
The original project plan lists PostgreSQL as the target database.
This module uses SQLite instead, as a working, zero-setup stand-in
that can be demoed immediately with no server to install.

Because every query goes through the functions below (no raw SQL
scattered across the app), moving to PostgreSQL later mainly means
swapping this file for one that talks to Postgres (e.g. via
SQLAlchemy or asyncpg) with the same function names.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "startup_intelligence.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                startup_idea TEXT,
                industry TEXT,
                location TEXT,
                input_json TEXT NOT NULL,
                analysis_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_report(startup_input: dict, analysis: dict) -> str:
    report_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO reports
                (id, created_at, startup_idea, industry, location, input_json, analysis_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                datetime.now(timezone.utc).isoformat(),
                startup_input.get("startup_idea"),
                startup_input.get("industry"),
                startup_input.get("location"),
                json.dumps(startup_input),
                json.dumps(analysis),
            ),
        )
        conn.commit()
        return report_id
    finally:
        conn.close()


def list_reports(limit: int = 50):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, created_at, startup_idea, industry, location
            FROM reports
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_report(report_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()

        if row is None:
            return None

        data = dict(row)
        return {
            "id": data["id"],
            "created_at": data["created_at"],
            "startup": json.loads(data["input_json"]),
            "analysis": json.loads(data["analysis_json"]),
        }
    finally:
        conn.close()


def delete_report(report_id: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
