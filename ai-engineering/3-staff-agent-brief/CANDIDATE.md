# Exercise: Triage and draft agent (2 hours)

Use your AI assistant however you like. There is no starter code. You are building this the way you would at work, and the interviewer plays the product manager.

## The brief

> Our support team gets about a few thousand inbound requests a day across email and chat. People spend most of their time reading, sorting and writing first replies. We want an agent that triages requests and drafts responses so the team can move faster. Build something we could pilot.

That is the whole brief. Ask the PM whatever you need to scope it. Decide what to build, what to leave out, and how you will know it works.

## What we have for you

- `data/sample_requests.jsonl`: 18 anonymized requests (fields: `id`, `channel`, `customer_tier`, `text`). They are representative, not exhaustive.
- A Python environment. You can use any libraries you like.
- A model: your interviewer will tell you whether an API key is available. If not, build against a mock and design for swapping in a real model.

## What to hand over

1. **A working vertical slice.** Something that takes a request and produces a triage decision and a draft. It does not need to be complete, but it must run.
2. **A way to measure quality.** Show us how you would know the agent is good enough to pilot, and how you would know when it regresses.
3. **A short `DESIGN.md`.** Key decisions and tradeoffs, risks, what you deliberately did not build, and what you would do next.

## Time plan (suggested)

| Time | Focus |
|---|---|
| 0–15 min | Questions and scoping with the PM |
| 15–90 min | Build the slice and the way to measure it |
| 90–105 min | Update for new information from the PM |
| 105–120 min | Walkthrough and discussion |
