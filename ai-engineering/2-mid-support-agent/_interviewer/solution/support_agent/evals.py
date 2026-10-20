"""Eval harness for the support agent (reference solution)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .llm import LLM, LLMReply, MockLLM
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
    report = EvalReport()
    for case in cases:
        try:
            agent = agent_factory(MockLLM(case.script))
            result = agent.run(case.user_message)
        except Exception as exc:  # one bad case must not stop the run
            report.results.append(CaseResult(case.name, False, f"raised {type(exc).__name__}: {exc}"))
            continue

        problems = []
        if result.stop_reason != case.expect_stop_reason:
            problems.append(f"stop_reason {result.stop_reason!r} != {case.expect_stop_reason!r}")
        if case.expect_answer_contains is not None and case.expect_answer_contains not in result.answer:
            problems.append(f"answer {result.answer!r} missing {case.expect_answer_contains!r}")
        if result.escalated != case.expect_escalated:
            problems.append(f"escalated {result.escalated} != {case.expect_escalated}")
        report.results.append(CaseResult(case.name, not problems, "; ".join(problems)))
    return report
