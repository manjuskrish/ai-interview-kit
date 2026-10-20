# Scoring sheet

Score each dimension 1–4 from what you observed live and from the AI transcript. Use the same sheet for every role and level; the exercise guides say what each score looks like for that exercise.

## Dimensions and starting weights

| Dimension | What it measures | Junior | Mid/Senior | Staff+ |
|---|---|---|---|---|
| Decomposition | Breaks the problem down before prompting instead of pasting it whole | 15% | 15% | 20% |
| Prompt and context | Gives the AI constraints, existing code and conventions; iterates | 15% | 20% | 10% |
| Verification | Reads the diff, runs the code, writes tests rather than trusting output | 30% | 25% | 15% |
| Recovery | Diagnoses wrong AI output and changes approach instead of re-asking | 25% | 15% | 10% |
| Design judgment | Spots over-engineering, insecurity and poor fit with the system | 5% | 15% | 30% |
| Ownership | Explains every line shipped and the tradeoffs behind it | 10% | 10% | 15% |

Weights are a starting point. Recalibrate after about ten pilot interviews.

## Scale

| Score | Label | Looks like |
|---|---|---|
| 1 | Not yet | Accepts AI output as is; cannot explain what the code does |
| 2 | Developing | Checks the happy path; needs prompting to find edge cases |
| 3 | Solid | Verifies independently and recovers when the AI is wrong |
| 4 | Exceptional | Anticipates AI failure modes and explains the tradeoffs |

## Proposed hiring bars

| Level | Bar |
|---|---|
| Junior | Weighted average 2.5+ and Verification at 3+ |
| Mid/Senior | Weighted average 3.0+ and no dimension below 2 |
| Staff+ | Weighted average 3.3+ and Design judgment at 4 |

Treat these as proposals. Compare them with hidden-test results and interviewer judgment during the pilot.

## Session record (copy per candidate)

```
Candidate:            Role / level:            Exercise:
Interviewer:          Date:                    AI tool used:
Transcript saved:  [ ]    Hidden tests run:  [ ]  (passed / total: __ / __)

Dimension            Score (1–4)   Evidence (quote, moment, or file)
Decomposition
Prompt and context
Verification
Recovery
Design judgment
Ownership

Weighted average:
Red flags observed:
Strongest moment:
Recommendation:  Strong no / No / Lean yes / Yes / Strong yes
```

## Scoring tips

- Score what you saw, not the final code. A candidate who ships a worse solution but caught three AI mistakes can outscore one who accepted a clean-looking answer.
- Note timestamps for the moments you cite so you can find them in the transcript.
- Run the hidden tests after the session, not during it. Treat them as evidence for Verification and Design judgment, not as a pass/fail gate.
- Score before you discuss with other interviewers.
