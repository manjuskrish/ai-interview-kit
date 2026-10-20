"""A tiny tool-calling agent loop (reference solution)."""
import json

from tools import TOOLS

MAX_PARSE_ATTEMPTS = 3
RETRY_PROMPT = 'Your last reply was not valid. Reply with JSON only: {"tool": ..., "args": {...}} or {"final": ...}.'


class AgentError(Exception):
    """Raised when the agent cannot produce an answer."""


def _parse(reply):
    try:
        action = json.loads(reply)
    except (TypeError, ValueError):
        return None
    if not isinstance(action, dict):
        return None
    if "final" in action:
        return action
    if isinstance(action.get("tool"), str) and isinstance(action.get("args", {}), dict):
        return action
    return None


def run_agent(llm, user_input, max_steps=5):
    messages = [{"role": "user", "content": user_input}]
    for _ in range(max_steps):
        action = None
        reply = ""
        for _attempt in range(MAX_PARSE_ATTEMPTS):
            reply = llm.complete(messages)
            action = _parse(reply)
            if action is not None:
                break
            messages.append({"role": "assistant", "content": str(reply)})
            messages.append({"role": "user", "content": RETRY_PROMPT})
        else:
            raise AgentError(f"model returned invalid replies {MAX_PARSE_ATTEMPTS} times")

        if "final" in action:
            return action["final"]

        name = action["tool"]
        args = action.get("args", {})
        try:
            if name not in TOOLS:
                raise KeyError(f"unknown tool {name!r}")
            result = TOOLS[name](**args)
        except Exception as exc:
            result = f"ERROR: {type(exc).__name__}: {exc}"

        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "tool", "content": str(result)})

    raise AgentError(f"no final answer after {max_steps} steps")
