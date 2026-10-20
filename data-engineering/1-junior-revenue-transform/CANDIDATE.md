# Exercise: Fix the revenue transform (45 minutes)

Use your AI assistant however you like. We want to see how you work with it. Talk through what you are doing as you go.

## Context

`transform.py` builds a **daily revenue report** from three tables:

| Table | Columns |
|---|---|
| `orders` | `order_id`, `customer_id`, `amount`, `currency`, `created_at` (ISO 8601 with a UTC offset), `ingested_at` |
| `customers` | `customer_id`, `region`, `updated_at` |
| `fx` | `date` (`YYYY-MM-DD`), `currency`, `rate_to_usd` |

`run.py` runs it on the sample CSVs in `data/`. The numbers look plausible but they are wrong. Run `pytest` and `python run.py` to start.

## Part 1: fix the transform (about 30 minutes)

`build_daily_revenue(orders, customers, fx)` must return a DataFrame with columns `date`, `region`, `order_count`, `revenue_usd`, sorted by `date` then `region`, with `revenue_usd` rounded to 2 decimals. Requirements:

1. **Dates are UTC.** Bucket each order by the UTC date of `created_at`, not the local date in the string. The output `date` is a `YYYY-MM-DD` string.
2. **Orders can be delivered more than once.** For a repeated `order_id`, keep the row with the latest `ingested_at`, whatever its position in the file.
3. **Each order is counted once.** Enriching with customer data must never change the number of orders. If a customer appears more than once, use the row with the latest `updated_at`.
4. **Unknown customers** are reported under region `UNKNOWN`. They are not dropped.
5. **FX rates.** Use the rate for the order's UTC date. If there is no rate for that date (for example weekends), use the most recent earlier rate for the same currency. If an order has no applicable rate at all, raise `ValueError` rather than silently dropping it.

## Part 2: prove it (about 10 minutes)

Show how you know the report is right. Add at least one test for a case the existing tests do not cover, and compare the order count and total revenue before and after your changes.

## Part 3: walk us through it (about 5 minutes)

Be ready to explain what was wrong, how you found each problem, and what checks you would put in a real pipeline.
