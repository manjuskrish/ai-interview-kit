"""Conversation memory: the messages sent to the model on each call (reference solution)."""
from __future__ import annotations


class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._messages: list[dict] = []

    def add(self, role: str, content: str, **extra) -> None:
        self._messages.append({"role": role, "content": content, **extra})

    def messages(self) -> list[dict]:
        """Return the newest max_messages messages."""
        return self._messages[-self.max_messages :]

    def __len__(self) -> int:
        return len(self._messages)
