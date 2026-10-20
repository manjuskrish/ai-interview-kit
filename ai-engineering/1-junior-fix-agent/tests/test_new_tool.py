import json

from agent import run_agent
from llm import ScriptedLLM


def tool(name, **args):
    return json.dumps({"tool": name, "args": args})


def final(text):
    return json.dumps({"final": text})


def test_get_order_status_is_available():
    llm = ScriptedLLM([tool("get_order_status", order_id="A100"), final("shipped")])
    assert run_agent(llm, "where is A100?") == "shipped"
    assert llm.seen[1][-1] == {"role": "tool", "content": "shipped"}


def test_unknown_order_is_reported_as_error():
    llm = ScriptedLLM([tool("get_order_status", order_id="ZZZ"), final("not found")])
    assert run_agent(llm, "where is ZZZ?") == "not found"
    assert llm.seen[1][-1]["content"].startswith("ERROR:")
