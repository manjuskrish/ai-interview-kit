# AI-Assisted Coding Interview Kit

Nine exercises for the 3×3 grid: three roles (AI Engineering, Cloud SWE, Data Engineering) at three levels (Junior, Mid/Senior, Staff+).
Candidates use an AI assistant (Claude Code in VS Code, or any tool you standardize on). You score how they **direct, verify and judge** the AI's output, not how fast they type.

| Role | Level | Format | Time | Folder |
|---|---|---|---|---|
| AI Engineering | Junior | 1 · Fix and modify | 45 min | `ai-engineering/1-junior-fix-agent` |
| AI Engineering | Mid/Senior | 2 · Complete and test | 90 min | `ai-engineering/2-mid-support-agent` |
| AI Engineering | Staff+ | 3 · Open-ended build | 120 min | `ai-engineering/3-staff-agent-brief` |
| Cloud SWE | Junior | 1 · Fix and modify | 45 min | `cloud-swe/1-junior-lambda-handler` |
| Cloud SWE | Mid/Senior | 2 · Complete and test | 90 min | `cloud-swe/2-mid-order-service` |
| Cloud SWE | Staff+ | 3 · Open-ended build | 120 min | `cloud-swe/3-staff-ingestion-platform` |
| Data Engineering | Junior | 1 · Fix and modify | 45 min | `data-engineering/1-junior-revenue-transform` |
| Data Engineering | Mid/Senior | 2 · Complete and test | 90 min | `data-engineering/2-mid-incremental-pipeline` |
| Data Engineering | Staff+ | 3 · Open-ended build | 120 min | `data-engineering/3-staff-cdc-lakehouse` |

## Quick start

1. Unzip, then open the folder in VS Code: `code ai-interview-kit`
2. Create an environment and install dependencies (Python 3.10+):
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Check the kit itself works. This runs every reference solution against its tests:
   ```bash
   scripts/verify_kit.sh
   ```
4. Read `interviewer/session-runbook.md` and `interviewer/scoring-sheet.md`.

No cloud accounts and no LLM API keys are needed. AWS is simulated with `moto`, the data exercises use pandas and SQLite, and the agent exercises use a scripted mock LLM.

## What is in each exercise folder

| Path | Who sees it | Purpose |
|---|---|---|
| `CANDIDATE.md` | Candidate | The brief and requirements |
| starter code and `tests/` | Candidate | Code with seeded issues and visible tests |
| `_interviewer/INTERVIEWER.md` | Interviewer | Seeded issues, AI traps, probes, scoring anchors |
| `_interviewer/solution/` | Interviewer | Reference solution (Formats 1 and 2) |
| `_interviewer/hidden_tests/` | Interviewer | Extra tests to run after the session (Formats 1 and 2) |

Format 3 exercises are open briefs, so they ship a stakeholder script and sample data instead of a solution.

## Handing an exercise to a candidate

```bash
scripts/make_candidate_pack.sh cloud-swe/2-mid-order-service
```

This writes `2-mid-order-service-candidate.zip` in the current directory, with the `_interviewer/` folder removed. Or open just that exercise folder in a fresh VS Code window on a machine that does not have the interviewer material.

## Using Claude Code with this kit

- To adapt the kit (change the stack, add exercises, tune the rubric), open the repo root and ask Claude Code. `CLAUDE.md` explains the layout and the rules for editing it.
- For a candidate session, open only the candidate pack so the assistant cannot see `_interviewer/`.
- Save the AI conversation for each session. Reviewing the transcript is part of scoring.

## Assumptions to change if needed

- Python for every role. Swap stacks per role by editing the starter code and tests.
- Claude Code is the assumed AI tool, but nothing in the exercises depends on it.
- Time boxes (45/90/120 minutes) are starting points.
