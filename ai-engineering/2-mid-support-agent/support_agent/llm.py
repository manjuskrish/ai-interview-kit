"""Model interface and a deterministic mock for tests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class LLMReply:
    kind: str  # "tool_call" or "final"
    text: str = ""  # the answer, for kind="final"
    tool: str = ""  # the tool name, for kind="tool_call"
    args: dict = field(default_factory=dict)
    tokens: int = 50  # tokens this reply "cost"


class LLM(Protocol):
    def complete(self, messages: list[dict]) -> LLMReply: ...


class MockLLM:
    """Replays scripted replies in order and records what it was sent."""

    def __init__(self, script: list[LLMReply]):
        self._script = list(script)
        self.calls: list[list[dict]] = []  # messages passed on each call

    def complete(self, messages: list[dict]) -> LLMReply:
        self.calls.append([dict(m) for m in messages])
        if not self._script:
            raise RuntimeError("MockLLM script exhausted")
        return self._script.pop(0)
