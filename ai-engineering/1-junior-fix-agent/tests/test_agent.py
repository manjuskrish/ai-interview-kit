import json

import pytest

from agent import AgentError, run_agent
from llm import ScriptedLLM


def tool(name, **args):
    return json.dumps({"tool": name, "args": args})


def final(text):
    return json.dumps({"final": text})


def test_returns_final_answer():
    llm = ScriptedLLM([final("hello")])
    assert run_agent(llm, "hi") == "hello"


def test_calls_tool_then_answers():
    llm = ScriptedLLM([tool("add", a=2, b=3), final("5")])
    assert run_agent(llm, "2+3?") == "5"
    assert llm.seen[1][-1] == {"role": "tool", "content": "5"}


def test_retries_invalid_json_then_succeeds():
    llm = ScriptedLLM(["not json", final("ok")])
    assert run_agent(llm, "hi") == "ok"
    assert llm.calls == 2


def test_gives_up_after_three_invalid_replies():
    llm = ScriptedLLM(["nope"])
    with pytest.raises(AgentError):
        run_agent(llm, "hi")
    assert llm.calls == 3


def test_tool_exception_is_reported_to_model():
    llm = ScriptedLLM([tool("add", a=1), final("recovered")])  # missing argument b
    assert run_agent(llm, "x") == "recovered"
    assert llm.seen[1][-1]["role"] == "tool"
    assert llm.seen[1][-1]["content"].startswith("ERROR:")


def test_unknown_tool_is_reported_to_model():
    llm = ScriptedLLM([tool("launch_rockets"), final("sorry")])
    assert run_agent(llm, "x") == "sorry"
    assert llm.seen[1][-1]["content"].startswith("ERROR:")


def test_stops_runaway_loop():
    llm = ScriptedLLM([tool("echo", text="again")])
    with pytest.raises(AgentError):
        run_agent(llm, "loop", max_steps=3)
    assert llm.calls == 3
