"""The support agent loop (reference solution)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from .llm import LLM
from .memory import ConversationMemory
from .tools import ToolError, ToolRegistry

FALLBACK_ANSWER = "Sorry, I couldn't complete this request."
ESCALATION_ANSWER = "I've passed this to a human agent who will follow up."


@dataclass
class AgentResult:
    answer: str
    steps: int
    tokens_used: int
    escalated: bool = False
    stop_reason: str = "final"  # final | escalated | max_steps | token_budget


class SupportAgent:
    def __init__(
        self,
        llm: LLM,
        registry: ToolRegistry,
        memory: ConversationMemory | None = None,
        max_steps: int = 6,
        token_budget: int = 1000,
        refund_limit: float = 100.0,
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.memory = memory or ConversationMemory()
        self.max_steps = max_steps
        self.token_budget = token_budget
        self.refund_limit = refund_limit

    def _refund_exceeds_limit(self, args: dict) -> bool:
        amount = args.get("amount")
        return isinstance(amount, (int, float)) and amount > self.refund_limit

    def run(self, user_message: str) -> AgentResult:
        self.memory.add("user", user_message)
        tokens_used = 0

        for step in range(1, self.max_steps + 1):
            reply = self.llm.complete(self.memory.messages())
            tokens_used += reply.tokens

            if tokens_used > self.token_budget:
                return AgentResult(FALLBACK_ANSWER, step, tokens_used, False, "token_budget")

            if reply.kind == "final":
                self.memory.add("assistant", reply.text)
                return AgentResult(reply.text, step, tokens_used, False, "final")

            if reply.kind != "tool_call":
                return AgentResult(FALLBACK_ANSWER, step, tokens_used, False, "max_steps")

            self.memory.add("assistant", "", tool=reply.tool, args=reply.args)

            if reply.tool == "escalate_to_human":
                self._call(reply.tool, reply.args)
                return AgentResult(ESCALATION_ANSWER, step, tokens_used, True, "escalated")

            if reply.tool == "issue_refund" and self._refund_exceeds_limit(reply.args):
                amount = reply.args["amount"]
                self._call("escalate_to_human", {"reason": f"refund of {amount} exceeds limit {self.refund_limit}"})
                return AgentResult(ESCALATION_ANSWER, step, tokens_used, True, "escalated")

            self.memory.add("tool", self._call(reply.tool, reply.args), tool=reply.tool)

        return AgentResult(FALLBACK_ANSWER, self.max_steps, tokens_used, False, "max_steps")

    def _call(self, tool: str, args: dict) -> str:
        try:
            return json.dumps(self.registry.call(tool, args))
        except ToolError as exc:
            return f"ERROR: {exc}"
