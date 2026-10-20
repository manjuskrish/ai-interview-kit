"""Warehouse schema (SQLite stands in for the real warehouse)."""
from __future__ import annotations

import sqlite3


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pipeline_state (
            name      TEXT PRIMARY KEY,
            watermark TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fact_events (
            id         TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            amount     REAL NOT NULL,
            event_ts   TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dq_failures (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT,
            rule   TEXT,
            detail TEXT
        );
        """
    )
    conn.commit()
