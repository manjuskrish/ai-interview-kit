from support_agent.llm import LLMReply, MockLLM
from support_agent.orchestrator import FALLBACK_ANSWER, SupportAgent
from support_agent.tools import build_default_registry


def tool_call(tool, **args):
    return LLMReply(kind="tool_call", tool=tool, args=args)


def final(text):
    return LLMReply(kind="final", text=text)


def make_agent(script, **kwargs):
    llm = MockLLM(script)
    return SupportAgent(llm, build_default_registry(), **kwargs), llm


def test_returns_final_answer():
    agent, _ = make_agent([final("Hello!")])
    result = agent.run("hi")
    assert result.answer == "Hello!"
    assert result.stop_reason == "final"
    assert result.steps == 1


def test_tool_result_is_fed_back_to_the_model():
    agent, llm = make_agent([tool_call("lookup_order", order_id="A100"), final("It has shipped.")])
    result = agent.run("where is A100?")
    assert result.answer == "It has shipped."
    last = llm.calls[1][-1]
    assert last["role"] == "tool"
    assert "shipped" in last["content"]


def test_tool_error_is_reported_to_the_model_not_raised():
    agent, llm = make_agent([tool_call("lookup_order", order_id="ZZZ"), final("Order not found.")])
    result = agent.run("where is ZZZ?")
    assert result.answer == "Order not found."
    assert llm.calls[1][-1]["content"].startswith("ERROR:")


def test_stops_at_max_steps():
    agent, llm = make_agent([tool_call("lookup_order", order_id="A100")] * 10, max_steps=3)
    result = agent.run("loop")
    assert result.stop_reason == "max_steps"
    assert result.steps == 3
    assert result.answer == FALLBACK_ANSWER
    assert len(llm.calls) == 3
