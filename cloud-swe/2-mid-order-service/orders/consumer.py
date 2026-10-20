"""SQS consumer. TODO(candidate): implement handle_batch()."""
from __future__ import annotations


def handle_batch(event: dict, repo=None, sqs=None) -> dict:
    """Process an SQS batch and return {"batchItemFailures": [...]}. See CANDIDATE.md, Part 2."""
    raise NotImplementedError("TODO(candidate)")
