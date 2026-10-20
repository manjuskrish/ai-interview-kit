"""The support agent loop. TODO(candidate): implement SupportAgent.run()."""
from __future__ import annotations

from dataclasses import dataclass

from .llm import LLM
from .memory import ConversationMemory
from .tools import ToolRegistry

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

    def run(self, user_message: str) -> AgentResult:
        raise NotImplementedError("TODO(candidate)")
