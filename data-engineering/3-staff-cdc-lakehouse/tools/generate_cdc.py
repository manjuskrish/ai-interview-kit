"""Generate a larger, messier CDC feed for the exercise.

Usage:
    python tools/generate_cdc.py --events 5000 --seed 7 > data/cdc_large.jsonl

The feed includes inserts, updates, deletes, duplicate deliveries, out-of-order delivery,
and a schema change (a new `coupon_code` column) after 60% of the events.
"""
import argparse
import json
import random

BASE_TS = 1714557600000  # 2024-05-01T10:00:00Z


def make_row(rng, pk, with_coupon):
    row = {
        "id": pk,
        "customer_id": f"c{rng.randint(1, 200)}",
        "status": "new",
        "amount": round(rng.uniform(5, 500), 2),
    }
    if with_coupon:
        row["coupon_code"] = rng.choice([None, None, "SAVE10", "WELCOME"])
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--disorder", type=float, default=0.05, help="fraction of events delivered out of order")
    parser.add_argument("--duplicates", type=float, default=0.02, help="fraction of events delivered twice")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    live, events, next_pk, lsn = {}, [], 1, 1000

    for i in range(args.events):
        lsn += 1
        v2 = i >= args.events * 0.6
        ts = BASE_TS + (lsn - 1000) * 250
        roll = rng.random()
        if not live or roll < 0.3:
            pk = next_pk
            next_pk += 1
            after = make_row(rng, pk, v2)
            live[pk] = after
            change = {"op": "c", "before": None, "after": after}
        elif roll < 0.85:
            pk = rng.choice(list(live))
            before = dict(live[pk])
            after = dict(before)
            after["status"] = rng.choice(["paid", "shipped", "refunded"])
            if rng.random() < 0.3:
                after["amount"] = round(rng.uniform(5, 500), 2)
            if v2 and "coupon_code" not in after:
                after["coupon_code"] = None
            live[pk] = after
            change = {"op": "u", "before": before, "after": after}
        else:
            pk = rng.choice(list(live))
            change = {"op": "d", "before": live.pop(pk), "after": None}
        events.append({"lsn": lsn, "ts_ms": ts, "source": {"table": "orders"}, **change})

    for _ in range(int(len(events) * args.duplicates)):
        events.append(dict(rng.choice(events)))

    for i in range(len(events) - 1):
        if rng.random() < args.disorder:
            j = min(len(events) - 1, i + rng.randint(1, 5))
            events[i], events[j] = events[j], events[i]

    for event in events:
        print(json.dumps(event))


if __name__ == "__main__":
    main()
