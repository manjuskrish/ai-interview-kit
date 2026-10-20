"""The incremental run (reference solution)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from .quality import DataQualityError, check_batch
from .state import StateStore, subtract_minutes
from .transform import clean, dedupe_latest


@dataclass
class RunResult:
    extracted: int  # rows fetched from the source
    loaded: int  # rows written to fact_events
    rejected: int  # rows rejected by clean()
    watermark: str  # the watermark after this run


_UPSERT = """
INSERT INTO fact_events (id, user_id, amount, event_ts, updated_at)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    user_id = excluded.user_id,
    amount = excluded.amount,
    event_ts = excluded.event_ts,
    updated_at = excluded.updated_at
WHERE excluded.updated_at >= fact_events.updated_at
"""


def load(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """Idempotent upsert. An older version never overwrites a newer one. Does not commit."""
    written = 0
    for r in rows:
        cursor = conn.execute(_UPSERT, (r["id"], r["user_id"], r["amount"], r["event_ts"], r["updated_at"]))
        written += cursor.rowcount
    return written


def _record_dq(conn: sqlite3.Connection, run_at: str, rule: str, detail: str) -> None:
    conn.execute("INSERT INTO dq_failures (run_at, rule, detail) VALUES (?, ?, ?)", (run_at, rule, detail))


def run_incremental(source, conn: sqlite3.Connection, name: str = "events", lookback_minutes: int = 60, now: str | None = None) -> RunResult:
    run_at = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    state = StateStore(conn, name)
    watermark = state.get_watermark()

    rows = source.fetch(updated_after=subtract_minutes(watermark, lookback_minutes))
    good, rejected = clean(rows)

    try:
        check_batch(len(rows), len(rejected))
    except DataQualityError as exc:
        for r in rejected:
            _record_dq(conn, run_at, r["reason"], str(r.get("id")))
        _record_dq(conn, run_at, "reject_rate", str(exc))
        conn.commit()
        raise

    try:
        for r in rejected:
            _record_dq(conn, run_at, r["reason"], str(r.get("id")))
        written = load(conn, dedupe_latest(good))
        new_watermark = max([watermark] + [r["updated_at"] for r in rows if r.get("updated_at")])
        state.set_watermark(new_watermark)
        conn.commit()  # data and watermark land together, or not at all
    except Exception:
        conn.rollback()
        raise

    return RunResult(len(rows), written, len(rejected), new_watermark)
