"""Row cleaning and de-duplication (reference solution)."""
from __future__ import annotations

REQUIRED = ("id", "user_id", "amount", "event_ts", "updated_at")


def _reject_reason(row: dict) -> str | None:
    for field in REQUIRED:
        if row.get(field) in (None, ""):
            return f"missing {field}"
    amount = row["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
        return "invalid amount"
    return None


def clean(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split rows into (good, rejected). Rejected rows carry a 'reason'."""
    good, rejected = [], []
    for row in rows:
        reason = _reject_reason(row)
        if reason:
            rejected.append({**row, "reason": reason})
        else:
            good.append(row)
    return good, rejected


def dedupe_latest(rows: list[dict]) -> list[dict]:
    """Keep one row per id: the version with the latest updated_at (later rows win ties)."""
    best: dict[str, dict] = {}
    for row in rows:
        current = best.get(row["id"])
        if current is None or row["updated_at"] >= current["updated_at"]:
            best[row["id"]] = row
    return list(best.values())
