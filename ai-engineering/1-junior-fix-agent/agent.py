"""A tiny tool-calling agent loop."""
import json

from tools import TOOLS


class AgentError(Exception):
    """Raised when the agent cannot produce an answer."""


def run_agent(llm, user_input, max_steps=5):
    messages = [{"role": "user", "content": user_input}]
    while True:
        reply = llm.complete(messages)
        action = json.loads(reply)

        if "final" in action:
            return action["final"]

        name = action["tool"]
        try:
            result = TOOLS[name](**action["args"])
        except Exception:
            result = None

        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "tool", "content": str(result)})
