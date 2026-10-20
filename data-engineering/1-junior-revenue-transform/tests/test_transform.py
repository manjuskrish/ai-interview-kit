import pandas as pd
import pytest

from transform import build_daily_revenue


def orders_df(*rows):
    cols = ["order_id", "customer_id", "amount", "currency", "created_at", "ingested_at"]
    return pd.DataFrame(rows, columns=cols)


def customers_df(*rows):
    return pd.DataFrame(rows, columns=["customer_id", "region", "updated_at"])


def fx_df(*rows):
    return pd.DataFrame(rows, columns=["date", "currency", "rate_to_usd"])


USD_FX = fx_df(("2024-03-01", "USD", 1.0), ("2024-03-02", "USD", 1.0))
ONE_CUSTOMER = customers_df(("c1", "AMER", "2024-01-01T00:00:00+00:00"))


def test_enrichment_does_not_change_the_order_count():
    orders = orders_df(("o1", "c1", 10.0, "USD", "2024-03-01T10:00:00+00:00", "2024-03-01T10:01:00+00:00"))
    customers = customers_df(
        ("c1", "EMEA", "2024-01-01T00:00:00+00:00"),
        ("c1", "AMER", "2024-02-01T00:00:00+00:00"),
    )

    report = build_daily_revenue(orders, customers, USD_FX)

    assert report["order_count"].sum() == 1
    assert report["revenue_usd"].sum() == pytest.approx(10.0)
    assert list(report["region"]) == ["AMER"]


def test_orders_are_bucketed_by_utc_date():
    # 23:30 at UTC-5 on March 1st is 04:30 UTC on March 2nd.
    orders = orders_df(("o1", "c1", 10.0, "USD", "2024-03-01T23:30:00-05:00", "2024-03-02T04:31:00+00:00"))

    report = build_daily_revenue(orders, ONE_CUSTOMER, USD_FX)

    assert list(report["date"]) == ["2024-03-02"]


@pytest.mark.parametrize("newest_first", [True, False])
def test_duplicate_orders_keep_the_latest_ingested_row(newest_first):
    # The result must not depend on which version comes first in the file.
    newer = ("o1", "c1", 25.0, "USD", "2024-03-01T10:00:00+00:00", "2024-03-01T10:05:00+00:00")
    older = ("o1", "c1", 20.0, "USD", "2024-03-01T10:00:00+00:00", "2024-03-01T10:01:00+00:00")
    orders = orders_df(newer, older) if newest_first else orders_df(older, newer)

    report = build_daily_revenue(orders, ONE_CUSTOMER, USD_FX)

    assert report["order_count"].sum() == 1
    assert report["revenue_usd"].sum() == pytest.approx(25.0)


def test_order_without_an_fx_rate_raises():
    orders = orders_df(("o1", "c1", 10.0, "JPY", "2024-03-01T10:00:00+00:00", "2024-03-01T10:01:00+00:00"))

    with pytest.raises(ValueError):
        build_daily_revenue(orders, ONE_CUSTOMER, USD_FX)
