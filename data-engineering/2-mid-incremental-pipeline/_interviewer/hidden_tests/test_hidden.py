import pytest

from pipeline import runner
from pipeline.runner import run_incremental
from pipeline.source import FakeSource
from pipeline.state import EPOCH, StateStore
from pipeline.transform import dedupe_latest


def row(id, updated, amount=10.0, event="2024-01-01T09:00:00", user="u1"):
    return {"id": id, "user_id": user, "amount": amount, "event_ts": event, "updated_at": updated}


def amount_of(conn, id):
    return conn.execute("SELECT amount FROM fact_events WHERE id = ?", (id,)).fetchone()[0]


def count(conn, table="fact_events"):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_dedupe_prefers_the_latest_updated_at_even_when_event_ts_ties():
    original = row("a", "2024-01-01T10:05:00", amount=10.0)
    correction = row("a", "2024-01-01T11:00:00", amount=12.0)  # same event_ts, newer updated_at

    assert dedupe_latest([original, correction]) == [correction]
    assert dedupe_latest([correction, original]) == [correction]


def test_a_correction_in_the_same_batch_wins(conn):
    source = FakeSource([row("a", "2024-01-01T10:05:00", amount=10.0), row("a", "2024-01-01T11:00:00", amount=12.0)])

    run_incremental(source, conn)

    assert amount_of(conn, "a") == 12.0


def test_an_older_version_never_overwrites_a_newer_one(conn):
    run_incremental(FakeSource([row("a", "2024-01-01T11:00:00", amount=12.0)]), conn)

    # A stale version surfaces later, inside the lookback window.
    run_incremental(FakeSource([row("a", "2024-01-01T10:30:00", amount=10.0)]), conn)

    assert amount_of(conn, "a") == 12.0
    assert StateStore(conn).get_watermark() == "2024-01-01T11:00:00"


def test_a_failed_load_rolls_back_data_and_watermark(conn, monkeypatch):
    def broken_load(connection, rows):
        connection.execute("INSERT INTO fact_events VALUES ('x', 'u', 1.0, '2024-01-01T09:00:00', '2024-01-01T10:00:00')")
        raise RuntimeError("disk full")

    monkeypatch.setattr(runner, "load", broken_load)

    with pytest.raises(RuntimeError):
        run_incremental(FakeSource([row("a", "2024-01-01T10:00:00")]), conn)

    assert count(conn) == 0
    assert StateStore(conn).get_watermark() == EPOCH


def test_rejected_rows_are_quarantined_and_the_watermark_moves_past_them(conn):
    rows = [row(f"r{i}", f"2024-01-01T10:0{i}:00") for i in range(9)]
    rows.append(row("bad", "2024-01-01T10:09:00", amount=None))

    result = run_incremental(FakeSource(rows), conn)

    assert result.loaded == 9
    assert result.rejected == 1
    assert count(conn, "dq_failures") == 1
    assert count(conn) == 9
    assert result.watermark == "2024-01-01T10:09:00"


def test_load_is_idempotent_and_never_commits_by_itself(conn):
    rows = [row("a", "2024-01-01T10:00:00"), row("b", "2024-01-01T10:01:00")]

    runner.load(conn, rows)
    runner.load(conn, rows)
    conn.rollback()  # load must not have committed

    assert count(conn) == 0
