# Interviewer guide: AI Engineering, Junior (Fix the agent)

**Time:** 45 minutes. **Tests:** reliability of a tool-calling loop, and whether the candidate verifies AI fixes.
**Most weighted:** Verification (30%), Recovery (25%).

## Setup (2 minutes)

Candidate runs `pytest` first. Expect 7 failures (5 in `test_agent.py`, 2 in `test_new_tool.py`) and 2 passes. The runaway-loop test fails with a `RuntimeError` from the `ScriptedLLM` safety net rather than hanging.

## Seeded issues

| Issue | Where | How it shows up | Visible test |
|---|---|---|---|
| Invalid JSON crashes the loop | `agent.py` `json.loads` | `JSONDecodeError` | yes |
| `max_steps` is ignored | `while True` | runaway loop | yes |
| Tool exceptions swallowed into `None` | `except Exception: result = None` | model sees `"None"` | yes |
| Unknown tool raises `KeyError` | `TOOLS[name]` | crash | yes |
| Missing `args` or `tool` key crashes | `action["args"]` | `KeyError` | hidden |
| Valid JSON with the wrong shape (a list, a string) | `"final" in action` | wrong behaviour or `TypeError` | hidden |
| Retries must not consume steps | design | step-count bug | hidden |

## AI traps to watch for

- **Retry that loops forever.** AI wraps `json.loads` in `try/except` and `continue`s with no attempt cap. The visible test catches it, but only if they run it.
- **Counting retries as steps.** Passes visible tests, fails the hidden `test_retries_do_not_consume_steps`.
- **Bare `except: pass` kept or moved.** Tool errors still hidden from the model.
- **Tests that only assert "no exception".** Weak verification.
- **Whole-file rewrite.** Large diff the candidate cannot explain. Ask about a specific line.

## Mid-session change (at about 30 minutes)

Say: "Product wants the agent to log every tool call with its duration and outcome. How would you add that without changing behaviour?" Watch whether they re-run the tests after the change and whether they keep the diff small.

## Probing questions

1. Why is swallowing a tool exception and sending `None` to the model a problem?
2. What happens if the model returns `{"tool": "echo"}` with no `args`?
3. Why do retries not count toward `max_steps`? What could go wrong if they did?
4. What would you log or monitor if this ran in production?
5. How would you test this against a real model instead of the script?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Verification | Runs tests after the AI's fix; stops when green | Reproduces each failure first; reads the diff; adds a test for a case not provided | Also tries malformed shapes (list, missing keys) unprompted |
| Recovery | Re-prompts with the same request when the AI's fix fails | Reads the failure and gives the AI the specific error and constraint | Spots the AI's retry-forever pattern before running it |
| Ownership | Explains the happy path | Explains each change and the retry semantics | Explains what to log, alert on and test against a real model |

## Reference materials

- `_interviewer/solution/` passes all visible tests.
- `_interviewer/hidden_tests/test_hidden.py` covers the hidden issues. Run it after the session.
