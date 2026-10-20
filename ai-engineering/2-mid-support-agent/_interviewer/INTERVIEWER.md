# Interviewer guide: AI Engineering, Mid/Senior (Support agent)

**Time:** 90 minutes. **Tests:** context-gathering, deterministic evals for a nondeterministic system, guardrails, spotting a latent bug in existing code.
**Most weighted:** Prompt and context (20%), Verification (25%), Design judgment (15%).

## Setup (3 minutes)

Candidate runs `pytest`. `test_memory.py` passes; the orchestrator and eval tests fail with `NotImplementedError`.

## Seeded issues

| Issue | Where | Notes |
|---|---|---|
| **Latent bug:** `memory.messages()` returns the *oldest* `max_messages`, not the newest | `memory.py` | The visible test passes. It only bites after 20+ messages, when the model stops seeing recent turns. An AI building on the existing code will not notice |
| Refund policy ambiguity | `CANDIDATE.md` | "Above the limit": is exactly 100.00 allowed? Is the limit per refund or cumulative per customer? A strong candidate asks. Hidden tests avoid the exact boundary |
| `issue_refund` does not enforce the limit itself | `tools.py` | The guardrail has to live in the orchestrator (or the candidate must justify moving it) |
| Escalation semantics | `CANDIDATE.md` | Does a tool error count as a step? (Yes: every model call is a step.) Does hitting a limit escalate? (No, by spec.) |
| Token budget check order | `CANDIDATE.md` | Must be checked before running the tool |

## AI traps to watch for

- **Trusting `memory.py`.** The candidate never reads it, or reads it and moves on. Prompt the question at the end: "What does `messages()` return when there are 30 messages?"
- **Real LLM or network calls in tests.** The spec gives a `MockLLM`; using anything else is a signal.
- **Guardrail only in the prompt.** Telling the model not to refund over $100 is not a guardrail.
- **Unbounded loops.** `while True` with a `break` on final.
- **Happy-path-only tests.** The Part 3 prompt asks for tests the repo lacks. Look for: tool error, step cap, token budget, refund over the limit, escalation, memory trimming.
- **Eval harness that swallows failures** or that stops at the first exception.

## Mid-session change (at about 55 minutes)

Say: "Support wants refunds over $100 to be allowed for customers marked as VIP, but only up to $250. How do you change this?" Watch whether they (a) find the one place the policy lives, (b) update tests first or alongside, and (c) ask where VIP status comes from.

## Probing questions

1. How would you evaluate this agent against a real model, where outputs vary?
2. What happens when the conversation passes 20 messages? Show me.
3. Where does the refund policy live and why there?
4. What would you log, and what would you never log?
5. How would you stop a prompt-injected tool result from triggering a refund?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Prompt and context | Pastes the stubs into the AI | Points the AI at existing modules, the spec and the test style | Also tells the AI the invariants (guardrails live in code, not prompts) and corrects it when it drifts |
| Verification | Runs the given tests | Writes tests for step cap, token budget, refund guardrail, tool error | Finds the memory bug without being asked, or tests trimming |
| Design judgment | Implements what the spec says | Notes the refund ambiguity and decides explicitly | Questions where guardrails belong and how evals scale |
| Ownership | Explains the loop | Explains each limit and stop reason | Explains failure modes in production (retries, budget blowups, injected tool output) |

## Reference materials

- `_interviewer/solution/` is a complete implementation (it also fixes `memory.py`).
- `_interviewer/hidden_tests/test_hidden.py` covers the memory bug, refund guardrail, token budget and escalation. Run it after the session.
