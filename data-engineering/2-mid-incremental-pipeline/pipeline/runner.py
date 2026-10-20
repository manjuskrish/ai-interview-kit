"""The incremental run. TODO(candidate): implement load() and run_incremental()."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class RunResult:
    extracted: int  # rows fetched from the source
    loaded: int  # rows written to fact_events
    rejected: int  # rows rejected by clean()
    watermark: str  # the watermark after this run


def load(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """Upsert rows into fact_events and return the number of rows written. Do NOT commit."""
    raise NotImplementedError("TODO(candidate)")


def run_incremental(source, conn: sqlite3.Connection, name: str = "events", lookback_minutes: int = 60, now: str | None = None) -> RunResult:
    """Run one incremental load. See CANDIDATE.md, Part 3."""
    raise NotImplementedError("TODO(candidate)")
