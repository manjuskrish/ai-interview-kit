"""Batch-level data-quality checks. TODO(candidate): implement check_batch()."""
from __future__ import annotations

MAX_REJECT_RATE = 0.2


class DataQualityError(Exception):
    """The batch is too dirty to load."""


def check_batch(total: int, rejected: int) -> None:
    """Raise DataQualityError if more than MAX_REJECT_RATE of a non-empty batch was rejected."""
    raise NotImplementedError("TODO(candidate)")
