"""A stand-in for the source system."""
from __future__ import annotations


class FakeSource:
    """Holds rows in memory. Tests can append to `rows` between runs."""

    def __init__(self, rows: list[dict] | None = None):
        self.rows: list[dict] = list(rows or [])

    def fetch(self, updated_after: str) -> list[dict]:
        """Rows whose updated_at is strictly after the given timestamp, oldest first."""
        matching = [r for r in self.rows if r.get("updated_at") and r["updated_at"] > updated_after]
        return sorted(matching, key=lambda r: (r["updated_at"], str(r.get("id"))))
