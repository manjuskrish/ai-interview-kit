from support_agent.llm import LLMReply, MockLLM
from support_agent.memory import ConversationMemory
from support_agent.orchestrator import ESCALATION_ANSWER, FALLBACK_ANSWER, SupportAgent
from support_agent.tools import ToolRegistry, lookup_order


def tool_call(tool, tokens=50, **args):
    return LLMReply(kind="tool_call", tool=tool, args=args, tokens=tokens)


def final(text, tokens=50):
    return LLMReply(kind="final", text=text, tokens=tokens)


def spy_registry():
    calls = []
    registry = ToolRegistry()
    registry.register("lookup_order", lookup_order)
    registry.register("issue_refund", lambda **a: calls.append(("refund", a)) or {"ok": True})
    registry.register("escalate_to_human", lambda reason: calls.append(("escalate", reason)) or {"ticket": "T-9"})
    return registry, calls


def test_memory_keeps_the_newest_messages():
    memory = ConversationMemory(max_messages=20)
    for i in range(25):
        memory.add("user", f"m{i}")
    contents = [m["content"] for m in memory.messages()]
    assert len(contents) == 20
    assert contents[-1] == "m24"
    assert contents[0] == "m5"


def test_refund_over_limit_is_escalated_and_not_executed():
    registry, calls = spy_registry()
    llm = MockLLM([tool_call("issue_refund", order_id="A101", amount=150.0)])
    result = SupportAgent(llm, registry).run("refund A101 please")
    assert result.escalated is True
    assert result.stop_reason == "escalated"
    assert result.answer == ESCALATION_ANSWER
    assert [c[0] for c in calls] == ["escalate"]
    assert "refund" in calls[0][1].lower()


def test_refund_under_limit_is_executed():
    registry, calls = spy_registry()
    llm = MockLLM([tool_call("issue_refund", order_id="A100", amount=40.0), final("Refunded.")])
    result = SupportAgent(llm, registry).run("refund A100")
    assert result.answer == "Refunded."
    assert [c[0] for c in calls] == ["refund"]


def test_escalate_tool_stops_the_run():
    registry, calls = spy_registry()
    llm = MockLLM([tool_call("escalate_to_human", reason="angry customer"), final("never reached")])
    result = SupportAgent(llm, registry).run("I want a manager")
    assert result.escalated is True
    assert result.stop_reason == "escalated"
    assert len(llm.calls) == 1


def test_token_budget_stops_before_running_the_tool():
    registry, calls = spy_registry()
    llm = MockLLM([tool_call("issue_refund", tokens=600, order_id="A100", amount=10.0)])
    result = SupportAgent(llm, registry, token_budget=500).run("refund")
    assert result.stop_reason == "token_budget"
    assert result.answer == FALLBACK_ANSWER
    assert calls == []


def test_unknown_tool_is_reported_to_the_model():
    registry, _ = spy_registry()
    llm = MockLLM([tool_call("drop_database"), final("Sorry.")])
    result = SupportAgent(llm, registry).run("x")
    assert result.answer == "Sorry."
    assert llm.calls[1][-1]["content"].startswith("ERROR:")


def test_agent_sends_newest_messages_when_history_is_long():
    registry, _ = spy_registry()
    memory = ConversationMemory(max_messages=4)
    for i in range(10):
        memory.add("user", f"old{i}")
    llm = MockLLM([final("ok")])
    SupportAgent(llm, registry, memory=memory).run("latest question")
    sent = llm.calls[0]
    assert sent[-1]["content"] == "latest question"
    assert len(sent) == 4
