"""Pipeline state: the watermark of the last successful run."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

EPOCH = "1970-01-01T00:00:00"
_FMT = "%Y-%m-%dT%H:%M:%S"


def subtract_minutes(ts: str, minutes: int) -> str:
    """ts minus N minutes. EPOCH stays EPOCH."""
    if ts <= EPOCH:
        return EPOCH
    return (datetime.strptime(ts, _FMT) - timedelta(minutes=minutes)).strftime(_FMT)


class StateStore:
    def __init__(self, conn: sqlite3.Connection, name: str = "events"):
        self.conn = conn
        self.name = name

    def get_watermark(self) -> str:
        row = self.conn.execute("SELECT watermark FROM pipeline_state WHERE name = ?", (self.name,)).fetchone()
        return row[0] if row else EPOCH

    def set_watermark(self, value: str) -> None:
        """Does NOT commit. The caller decides when the transaction ends."""
        self.conn.execute(
            "INSERT INTO pipeline_state (name, watermark) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET watermark = excluded.watermark",
            (self.name, value),
        )
