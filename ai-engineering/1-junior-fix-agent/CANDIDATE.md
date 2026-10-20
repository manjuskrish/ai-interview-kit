# Exercise: Fix the agent (45 minutes)

Use your AI assistant however you like. We want to see how you work with it. Talk through what you are doing as you go.

## Context

`agent.py` is a small tool-calling loop. The model replies with a JSON string, either:

- `{"tool": "<name>", "args": {...}}` to run a tool and feed the result back, or
- `{"final": "<answer>"}` when it is done.

`llm.py` has a `ScriptedLLM` that the tests use, so no API key is needed. `tools.py` holds the tools.

Start by running `pytest` and reading the failures.

## Part 1: make the loop reliable (about 25 minutes)

1. **Invalid replies.** If the model's reply is not valid JSON, retry. Allow 3 attempts in total (1 try plus 2 retries). Before each retry, append the bad reply (role `assistant`) and a `user` message asking the model to reply with JSON only. After 3 invalid replies, raise `AgentError`. Valid JSON that is not one of the two shapes above also counts as invalid.
2. **Tool failures.** An unknown tool, bad arguments, or an exception inside a tool must not crash the agent and must not be hidden. Append a `tool` message whose content starts with `ERROR:` and let the model recover.
3. **Runaway loops.** `max_steps` is the maximum number of valid model replies. Retries for invalid replies do not count as steps. If there is no `final` answer after `max_steps` replies, raise `AgentError`.

## Part 2: add a tool (about 15 minutes)

Add a `get_order_status(order_id)` tool that returns the status from the `ORDERS` dict in `tools.py`. Register it so the agent can call it. An unknown order must reach the model as an `ERROR:` message, like any other tool failure.

## Part 3: walk us through it (about 5 minutes)

Be ready to explain what you changed and why, how you know it works, and what you would add before shipping this.
