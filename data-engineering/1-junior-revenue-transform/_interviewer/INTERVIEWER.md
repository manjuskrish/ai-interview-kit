# Interviewer guide: Data Engineering, Junior (Revenue transform)

**Time:** 45 minutes. **Tests:** spotting silent data bugs (fan-out, timezones, dedupe, missing rates) and proving a fix with counts, not by eyeballing.
**Most weighted:** Verification (30%), Recovery (25%).

## Setup (2 minutes)

Candidate runs `python run.py` and `pytest`. The report "looks fine". Four visible tests fail and one passes. The dedupe test runs with the newer row first and last: the newer-first case passes by luck on the starter code, which is why the test is parametrized. Point out nothing; let them find that the order count and revenue do not reconcile with the input.

## Seeded issues

| Issue | Where | How it shows up | Visible test |
|---|---|---|---|
| **Join fan-out:** `customers` has several rows per customer, so the merge duplicates orders | `orders.merge(customers, ...)` | `order_count` and revenue inflated for `c1` | yes |
| **Local date, not UTC:** `created_at.str[:10]` takes the date in the string | `order_date` | `o2` lands on March 1 instead of March 2 | yes |
| **Non-deterministic dedupe:** `drop_duplicates` keeps the first row in file order, not the latest `ingested_at` | `drop_duplicates("order_id")` | `o3` reports 20.00 instead of 25.00 | yes |
| **Missing FX rates:** weekend dates have no rate, so revenue becomes NaN and `sum()` silently skips it | `merge(fx, ...)` | revenue understated; no error | yes (missing rate raises) |
| Unknown customers show as NaN region | `groupby(..., dropna=False)` | `o6` (customer `c4`) has a NaN region | hidden |
| Output not sorted or rounded | return value | unstable ordering | hidden |

## AI traps to watch for

- **`distinct()` or `drop_duplicates()` after the join.** Hides the fan-out without fixing the cause, and can drop legitimately distinct orders.
- **`drop_duplicates(keep="last")` without sorting.** Depends on file order; the visible test is built to catch this.
- **`fillna(0)` on revenue.** Turns a missing rate into a silent zero.
- **Converting dates with `pd.to_datetime` without `utc=True`**, or `.dt.date` after tz-naive parsing.
- **No before/after counts.** Passing the visible tests is not the same as reconciling the totals.
- **Whole-file rewrite** the candidate cannot explain.

## Mid-session change (at about 30 minutes)

Part 2 is the change. Watch whether they check order counts and total revenue against an independent calculation, rather than reusing the transform's own output.

## Probing questions

1. How would you have caught the fan-out without being told?
2. Why do we raise on a missing FX rate instead of using zero or dropping the row?
3. Which timezone should "a day" be in for a global business, and who decides?
4. What checks would you add so this fails loudly in production?
5. What happens at 100 million orders? Would you change anything?

## What the scores look like

| Dimension | 2: Developing | 3: Solid | 4: Exceptional |
|---|---|---|---|
| Verification | Runs the tests and checks the output looks plausible | Reconciles row counts and totals before and after each fix; adds a test for a case not provided | Builds an independent check (input total versus report total) and tests unknown customers and edge dates |
| Recovery | Re-prompts when a fix fails | Reads the failing assertion and gives the AI the specific cause | Spots the AI hiding a bug (`distinct`, `fillna(0)`) and rejects it |
| Ownership | Explains the fixes | Explains why each bug produced wrong numbers | Proposes pipeline-level checks (row-count reconciliation, null-rate and freshness alerts) |

## Reference materials

- `_interviewer/solution/transform.py` passes all visible tests.
- `_interviewer/hidden_tests/test_hidden.py` covers weekend rates, unknown customers, sorting and rounding. All of these are in the written requirements. Run it after the session.
