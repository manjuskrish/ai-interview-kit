"""Batch-level data-quality checks (reference solution)."""
from __future__ import annotations

MAX_REJECT_RATE = 0.2


class DataQualityError(Exception):
    """The batch is too dirty to load."""


def check_batch(total: int, rejected: int) -> None:
    if total > 0 and rejected / total > MAX_REJECT_RATE:
        raise DataQualityError(f"{rejected} of {total} rows rejected (limit {MAX_REJECT_RATE:.0%})")
