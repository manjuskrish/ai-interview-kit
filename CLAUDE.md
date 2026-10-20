# Interview kit: notes for Claude Code

This repo is an interview kit, not a product. It holds nine exercises (3 roles × 3 levels) plus interviewer material.

## Layout

- `<role>/<n>-<level>-<name>/` is one exercise.
  - `CANDIDATE.md`, starter code and `tests/` are candidate-facing.
  - `_interviewer/` is interviewer-only: guide, reference solution, hidden tests.
- `interviewer/` holds the shared scoring sheet and session runbook.
- `scripts/verify_kit.sh` runs each reference solution against visible and hidden tests.
- `scripts/make_candidate_pack.sh <exercise>` zips an exercise without `_interviewer/`.

## Rules when editing

- The starter code must keep its seeded bugs. Do not fix them in the candidate-facing files.
- Put fixes in `_interviewer/solution/`, mirroring the starter paths.
- Anything that reveals a seeded bug or a hidden requirement belongs only in `_interviewer/`.
- After changing an exercise, run `scripts/verify_kit.sh`. Every reference solution must pass.
- Starter tests are expected to fail on the starter code (that is the exercise). They must pass on the solution.
- Keep exercises deterministic: no network, no real LLM calls, no cloud accounts.

## Conventions

- Python 3.10+, pytest. Each exercise has its own `pytest.ini`; run `pytest` from inside the exercise folder.
- Rubric dimensions: Decomposition, Prompt and context, Verification, Recovery, Design judgment, Ownership. See `interviewer/scoring-sheet.md`.
