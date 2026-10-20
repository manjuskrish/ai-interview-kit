import json

import pytest

from agent import AgentError, run_agent
from llm import ScriptedLLM


def tool(name, **args):
    return json.dumps({"tool": name, "args": args})


def final(text):
    return json.dumps({"final": text})


def test_valid_json_with_wrong_shape_is_retried():
    llm = ScriptedLLM(["[1, 2, 3]", '"just a string"', final("ok")])
    assert run_agent(llm, "hi") == "ok"
    assert llm.calls == 3


def test_missing_args_is_reported_not_raised():
    llm = ScriptedLLM([json.dumps({"tool": "echo"}), final("recovered")])
    assert run_agent(llm, "x") == "recovered"
    assert llm.seen[1][-1]["content"].startswith("ERROR:")


def test_retries_do_not_consume_steps():
    llm = ScriptedLLM(["bad", "bad", tool("echo", text="x"), final("done")])
    assert run_agent(llm, "x", max_steps=2) == "done"


def test_bad_reply_and_retry_prompt_are_sent_back_to_model():
    llm = ScriptedLLM(["not json", final("ok")])
    run_agent(llm, "hi")
    retry_messages = llm.seen[1]
    assert retry_messages[-2] == {"role": "assistant", "content": "not json"}
    assert retry_messages[-1]["role"] == "user"


def test_final_answer_within_step_limit_is_returned():
    llm = ScriptedLLM([tool("echo", text="a"), tool("echo", text="b"), final("done")])
    assert run_agent(llm, "x", max_steps=3) == "done"


def test_step_limit_raises():
    llm = ScriptedLLM([tool("echo", text="a")])
    with pytest.raises(AgentError):
        run_agent(llm, "x", max_steps=2)
