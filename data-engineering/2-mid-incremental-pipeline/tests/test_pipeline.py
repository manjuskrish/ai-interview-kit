import pytest

from pipeline.quality import DataQualityError
from pipeline.runner import run_incremental
from pipeline.source import FakeSource
from pipeline.state import EPOCH, StateStore


def row(id, updated, amount=10.0, event="2024-01-01T09:00:00", user="u1"):
    return {"id": id, "user_id": user, "amount": amount, "event_ts": event, "updated_at": updated}


def count(conn, table="fact_events"):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_first_run_loads_everything_and_sets_the_watermark(conn):
    source = FakeSource([row("a", "2024-01-01T10:00:00"), row("b", "2024-01-01T10:05:00"), row("c", "2024-01-01T10:10:00")])

    result = run_incremental(source, conn)

    assert result.loaded == 3
    assert result.watermark == "2024-01-01T10:10:00"
    assert count(conn) == 3
    assert StateStore(conn).get_watermark() == "2024-01-01T10:10:00"


def test_rerunning_is_idempotent(conn):
    source = FakeSource([row("a", "2024-01-01T10:00:00"), row("b", "2024-01-01T10:05:00")])

    run_incremental(source, conn)
    run_incremental(source, conn)

    assert count(conn) == 2
    assert StateStore(conn).get_watermark() == "2024-01-01T10:05:00"


def test_a_late_arriving_row_inside_the_lookback_window_is_loaded(conn):
    source = FakeSource([row("a", "2024-01-01T10:00:00"), row("b", "2024-01-01T11:00:00")])
    run_incremental(source, conn)

    # Arrives after the watermark moved to 11:00, but its updated_at is 10:30.
    source.rows.append(row("late", "2024-01-01T10:30:00"))
    run_incremental(source, conn)

    assert count(conn) == 3


def test_a_dirty_batch_fails_loudly_and_changes_nothing(conn):
    bad = [row(f"bad{i}", f"2024-01-01T10:0{i}:00", amount=None) for i in range(3)]
    source = FakeSource([row("ok", "2024-01-01T10:09:00")] + bad)

    with pytest.raises(DataQualityError):
        run_incremental(source, conn)

    assert count(conn) == 0
    assert StateStore(conn).get_watermark() == EPOCH
    assert count(conn, "dq_failures") >= 1


def test_an_empty_extract_leaves_the_watermark_alone(conn):
    run_incremental(FakeSource([row("a", "2024-01-01T10:00:00")]), conn)

    result = run_incremental(FakeSource([]), conn)

    assert result.extracted == 0
    assert result.loaded == 0
    assert result.watermark == "2024-01-01T10:00:00"
    assert StateStore(conn).get_watermark() == "2024-01-01T10:00:00"
