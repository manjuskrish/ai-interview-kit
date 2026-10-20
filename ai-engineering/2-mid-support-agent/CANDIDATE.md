# Exercise: Complete the support agent (90 minutes)

Use your AI assistant however you like. We want to see how you work with it. Ask us questions whenever the spec is unclear.

## Context

`support_agent/` is a customer-support agent skeleton. The model (mocked in tests) either calls a tool or gives a final answer. The pieces:

| File | State |
|---|---|
| `llm.py` | Done. `LLMReply` and a deterministic `MockLLM` that replays a script |
| `tools.py` | Done. `ToolRegistry` plus demo tools (`lookup_order`, `issue_refund`, `escalate_to_human`) |
| `memory.py` | Done. `ConversationMemory` holds the messages sent to the model |
| `orchestrator.py` | **Incomplete.** `SupportAgent.run()` is not implemented |
| `evals.py` | **Incomplete.** `run_eval()` is not implemented |

Read the existing code first, then run `pytest`.

## Part 1: the agent loop (about 40 minutes)

Implement `SupportAgent.run(user_message) -> AgentResult`.

- Add the user message to memory, then loop: call `llm.complete(memory.messages())`.
- A `final` reply ends the run with `stop_reason="final"`.
- A `tool_call` reply runs the tool through the registry. Feed the result back to the model as a `tool` message. If the tool raises `ToolError`, send `ERROR: <message>` to the model instead of crashing.
- Every model call is one step. After `max_steps` steps without a final answer, stop with `stop_reason="max_steps"`.
- Each reply has a `tokens` cost. If the running total exceeds `token_budget`, stop with `stop_reason="token_budget"` and do not run that reply's tool.
- When the agent stops because of a limit it returns `AgentResult(answer=FALLBACK_ANSWER, ...)`. It must not raise.
- Calling `escalate_to_human` stops the run with `escalated=True`, `stop_reason="escalated"` and `ESCALATION_ANSWER` as the answer.

### Refund policy

Refunds above `refund_limit` (default 100.00) need a human. The agent must not execute `issue_refund` for those. Instead it calls `escalate_to_human` with a reason that mentions the refund, and stops as escalated.

## Part 2: an eval harness (about 25 minutes)

Implement `run_eval(cases, agent_factory) -> EvalReport` in `evals.py`. Each `EvalCase` carries a user message and a scripted model. The harness must run every case, check the expectations on the case, and report which passed and why any failed. One case raising an exception must not stop the others.

## Part 3: tests (about 15 minutes)

Add tests for behaviour the existing tests do not cover. Focus on the cases most likely to hurt in production.

## Part 4: walk us through it (about 10 minutes)

Be ready to explain your design, anything in the spec you had to interpret, and what you would add before shipping.
