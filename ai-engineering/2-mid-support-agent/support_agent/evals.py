"""Eval harness for the support agent. TODO(candidate): implement run_eval()."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .llm import LLM, LLMReply
from .orchestrator import SupportAgent


@dataclass
class EvalCase:
    name: str
    user_message: str
    script: list[LLMReply]  # what the mock model will say
    expect_stop_reason: str = "final"
    expect_answer_contains: str | None = None
    expect_escalated: bool = False


@dataclass
class CaseResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class EvalReport:
    results: list[CaseResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return len(self.results) - self.passed

    def summary(self) -> str:
        lines = [f"{self.passed}/{len(self.results)} passed"]
        lines += [f"FAIL {r.name}: {r.detail}" for r in self.results if not r.passed]
        return "\n".join(lines)


def run_eval(cases: list[EvalCase], agent_factory: Callable[[LLM], SupportAgent]) -> EvalReport:
    """Run every case with a fresh agent and a mock model, and report the outcomes."""
    raise NotImplementedError("TODO(candidate)")
