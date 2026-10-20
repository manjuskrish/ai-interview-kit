"""A scripted stand-in for a real model, used by the tests."""

MAX_CALLS = 50  # safety net so a runaway loop fails fast instead of hanging


class ScriptedLLM:
    """Replays canned replies in order. Repeats the last reply once the script runs out."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
        self.seen = []  # the messages passed on each call, for assertions

    def complete(self, messages):
        if self.calls >= MAX_CALLS:
            raise RuntimeError(f"ScriptedLLM called {MAX_CALLS} times: runaway loop?")
        self.seen.append([dict(m) for m in messages])
        reply = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return reply
