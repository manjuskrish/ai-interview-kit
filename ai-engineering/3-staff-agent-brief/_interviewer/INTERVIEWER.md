# Interviewer guide: AI Engineering, Staff+ (Triage and draft agent)

**Time:** 120 minutes. **Tests:** scoping, eval strategy, safety and failure handling, cost and latency, judgment about what not to build.
**Most weighted:** Design judgment (30%), Decomposition (20%), Ownership (15%).

You play the PM (call yourself "Dana"). Answer like a busy PM: short, honest, a bit vague until pushed. Reveal hidden facts only when asked a question that gets near them.

## Stakeholder script

| If they ask about... | Dana says |
|---|---|
| Volume | About 4,000 requests a day, spiky on Mondays and after incidents |
| Goal and success | Cut median time to first reply from about 4 hours to under 1 hour, without hurting CSAT. Nobody has defined a number for "good enough" yet; push them to propose one |
| Who uses the output | Support agents. A human reviews every draft in the pilot. No auto-send |
| Channels | Email and chat. Same pipeline is fine for the pilot |
| Languages | Mostly English, around 15% Spanish. Others rare |
| Categories | Billing, account access, technical issues, feature requests, security, legal/privacy, other. The team has no clean taxonomy; they would like the agent to suggest one |
| Data | Requests contain customer PII and occasionally payment details. Payment card numbers must never be stored or sent to a third-party model |
| Existing systems | Zendesk for tickets, a knowledge base in Confluence, billing in Stripe. All reachable by API. Do not let them assume integrations are free |
| Policy | Refunds over $100 need human approval. Never promise a refund, a date or a legal position in a draft |
| Prompt injection | Dana has not thought about it. If asked: "Customers can write anything." |
| Latency | Drafts should appear within about 30 seconds of arrival |
| Budget | Pilot budget is roughly $2,000 a month for model spend. Ask them to estimate |
| Labeled data | 6 months of historical tickets with final categories and agent replies, but quality varies |
| Pilot scope | One team of 12 agents, 4 weeks |

## Hidden facts (reveal only if asked)

- Security reports must go to a separate team within 15 minutes.
- Enterprise customers have contractual response times (1 hour).
- Legal and privacy requests (GDPR deletion, legal threats) must be handled by a named team and never auto-drafted.
- Duplicate follow-ups (like r01 and r15) should be linked, not triaged twice.

## Mid-session changes

Introduce these in order, about 75–90 minutes in:

1. "Legal just told us drafts can't include anything that sounds like a commitment on refunds or contracts. Can your design guarantee that?"
2. "We're launching to all customers in two months. Volume will be 10x. What changes?"
3. (If time) "The VP wants this to auto-send for free-tier feature requests. Thoughts?"

## What to look for

**Scoping (first 15 minutes)**
- Asks about success metrics, volume, who reviews the output, data sensitivity, policy limits.
- Proposes a narrow pilot slice instead of building everything.
- States assumptions out loud.

**Design**
- Triage and drafting treated as separate steps with different risk.
- Human-in-the-loop by default; explicit confidence and escalation rules.
- Handles PII and card data before the model sees it.
- Prompt injection treated as expected input (r05), not an edge case.
- Policy rules enforced in code or output checks, not only in the prompt.
- Idempotency and duplicates (r01 vs r15). Cost and latency estimates with real numbers.

**Evaluation**
- Builds a labeled set from the sample data and history, with a failure taxonomy.
- Separates triage accuracy from draft quality; uses rules and LLM judges where each fits.
- Plans regression checks and a pilot success gate.

**AI use**
- Uses AI to scaffold quickly, then reviews it.
- Stops the AI from over-engineering (multi-agent frameworks, vector databases) before it is needed.

## Red flags

- Starts coding before asking a single question.
- Chooses a framework before the problem.
- Eyeballs outputs on three examples and declares it works.
- Sends PII or card numbers to the model without comment.
- Cannot say what they left out of the pilot or why.
- Cannot explain code the AI generated.

## Probing questions

1. If this agent is wrong 5% of the time, who gets hurt and how?
2. How would you evaluate a draft when two good replies can look very different?
3. What do you do with r05? With r11? With r12?
4. What would you instrument in week one of the pilot?
5. What would make you shut the pilot down?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Decomposition | Builds one prompt that does everything | Separates triage, retrieval, draft and review | Sequences the build so a safe slice ships first |
| Design judgment | Follows the brief | Surfaces risks (PII, injection, policy) and designs for them | Makes explicit tradeoffs with numbers; pushes back on the auto-send idea |
| Verification | A few manual examples | Labeled set, metrics, failure taxonomy | Regression gates, pilot success criteria, monitoring |
| Ownership | Explains the demo | Explains every decision and gap | Gives a rollout plan with kill criteria |
