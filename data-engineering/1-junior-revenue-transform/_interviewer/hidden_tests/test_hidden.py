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


CUSTOMERS = customers_df(("c1", "AMER", "2024-01-01T00:00:00+00:00"), ("c2", "EMEA", "2024-01-01T00:00:00+00:00"))


def test_weekend_orders_use_the_most_recent_earlier_rate():
    # March 2, 2024 is a Saturday: no rate that day, so the Friday rate applies.
    fx = fx_df(("2024-03-01", "EUR", 1.10), ("2024-03-04", "EUR", 1.20))
    orders = orders_df(("o1", "c1", 100.0, "EUR", "2024-03-02T12:00:00+00:00", "2024-03-02T12:01:00+00:00"))

    report = build_daily_revenue(orders, CUSTOMERS, fx)

    assert report["revenue_usd"].sum() == pytest.approx(110.0)


def test_unknown_customers_are_reported_not_dropped():
    fx = fx_df(("2024-03-01", "USD", 1.0))
    orders = orders_df(("o1", "c9", 40.0, "USD", "2024-03-01T12:00:00+00:00", "2024-03-01T12:01:00+00:00"))

    report = build_daily_revenue(orders, CUSTOMERS, fx)

    assert list(report["region"]) == ["UNKNOWN"]
    assert report["order_count"].sum() == 1


def test_output_columns_sorting_and_rounding():
    fx = fx_df(("2024-03-01", "USD", 1.0), ("2024-03-02", "USD", 1.0))
    orders = orders_df(
        ("o1", "c2", 10.004, "USD", "2024-03-02T01:00:00+00:00", "2024-03-02T01:01:00+00:00"),
        ("o2", "c1", 5.0, "USD", "2024-03-01T01:00:00+00:00", "2024-03-01T01:01:00+00:00"),
        ("o3", "c2", 3.0, "USD", "2024-03-01T02:00:00+00:00", "2024-03-01T02:01:00+00:00"),
    )

    report = build_daily_revenue(orders, CUSTOMERS, fx)

    assert list(report.columns) == ["date", "region", "order_count", "revenue_usd"]
    assert list(zip(report["date"], report["region"])) == [
        ("2024-03-01", "AMER"),
        ("2024-03-01", "EMEA"),
        ("2024-03-02", "EMEA"),
    ]
    assert report["revenue_usd"].tolist() == [5.0, 3.0, 10.0]


def test_orders_on_either_side_of_utc_midnight_land_on_different_days():
    fx = fx_df(("2024-03-01", "USD", 1.0), ("2024-03-02", "USD", 1.0))
    orders = orders_df(
        ("o1", "c1", 1.0, "USD", "2024-03-01T23:59:59+00:00", "2024-03-02T00:01:00+00:00"),
        ("o2", "c1", 1.0, "USD", "2024-03-02T00:00:00+00:00", "2024-03-02T00:01:00+00:00"),
    )

    report = build_daily_revenue(orders, CUSTOMERS, fx)

    assert report["date"].tolist() == ["2024-03-01", "2024-03-02"]
    assert report["order_count"].tolist() == [1, 1]


def test_sample_data_reconciles():
    orders = pd.read_csv("data/orders.csv")
    customers = pd.read_csv("data/customers.csv")
    fx = pd.read_csv("data/fx_rates.csv")

    report = build_daily_revenue(orders, customers, fx)

    assert report["order_count"].sum() == orders["order_id"].nunique() == 7
