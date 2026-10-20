from support_agent.evals import EvalCase, run_eval
from support_agent.llm import LLMReply
from support_agent.orchestrator import SupportAgent
from support_agent.tools import build_default_registry


def factory(llm):
    return SupportAgent(llm, build_default_registry())


def test_run_eval_reports_passes_and_failures():
    cases = [
        EvalCase("greets", "hi", [LLMReply(kind="final", text="Hello!")], expect_answer_contains="Hello"),
        EvalCase("wrong", "hi", [LLMReply(kind="final", text="Goodbye")], expect_answer_contains="Hello"),
    ]
    report = run_eval(cases, factory)
    assert report.passed == 1
    assert report.failed == 1
    assert [r.name for r in report.results if not r.passed] == ["wrong"]


def test_run_eval_captures_exceptions_and_keeps_going():
    cases = [
        EvalCase("boom", "hi", []),  # empty script: the mock model raises
        EvalCase("ok", "hi", [LLMReply(kind="final", text="Hello!")]),
    ]
    report = run_eval(cases, factory)
    assert report.failed == 1
    assert report.passed == 1
    assert "RuntimeError" in report.results[0].detail
