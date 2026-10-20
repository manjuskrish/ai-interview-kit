# Session runbook

## Before the session

- Pick the exercise for the role and level. Hand the candidate only the candidate pack (`scripts/make_candidate_pack.sh`).
- Confirm the AI tool works on the candidate's machine and that its conversation history is saved.
- Run `pytest` once yourself so you know the starting failures.
- Read `_interviewer/INTERVIEWER.md` for the exercise.

## Opening (5 minutes)

Say, in your own words:

- "Use your AI assistant however you normally would. We want to see how you work with it."
- "Think out loud. Tell us when you accept, edit or throw away what it gives you."
- "Ask me questions any time. I'll answer like a teammate or stakeholder would."

## During the session

| Moment | What to do |
|---|---|
| First 5–10 minutes | Watch whether they read the code and run the tests before prompting |
| When they accept AI output | Do not hint. Note whether they read the diff and run it |
| When something breaks | Note whether they diagnose it or re-prompt blindly |
| About 60% through | Introduce the exercise's mid-session change (see its guide) |
| If they are stuck for 5+ minutes | Give one nudge, and record that you did |

Answer clarifying questions honestly. For Format 3, play the stakeholder from the script and reveal hidden requirements only when asked.

## Last 10 minutes: walkthrough

Ask every candidate:

1. Walk me through the change you are most confident in. Why?
2. Which part of the AI's output did you not trust, and what did you do about it?
3. What would you check before shipping this?
4. What did the AI get wrong today?

Then ask the exercise-specific probes from its guide.

## After the session

1. Save the transcript and the final repo state.
2. Run the hidden tests (Formats 1 and 2) and record the result.
3. Fill in the session record in `scoring-sheet.md` before talking to anyone else.

## Fairness

- Same exercise and time box for every candidate at a given role and level.
- Same nudge policy: one nudge after five stuck minutes, recorded.
- Do not penalize a candidate for using the AI heavily. Penalize accepting output without checking it.
- Do not reward a candidate for avoiding the AI. The skill is directing it well.
