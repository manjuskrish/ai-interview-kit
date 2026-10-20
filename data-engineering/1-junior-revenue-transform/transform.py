"""Builds the daily revenue report."""
import pandas as pd


def build_daily_revenue(orders: pd.DataFrame, customers: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    orders = orders.drop_duplicates("order_id").copy()
    orders["order_date"] = orders["created_at"].str[:10]

    df = orders.merge(customers, on="customer_id", how="left")
    df = df.merge(fx, left_on=["order_date", "currency"], right_on=["date", "currency"], how="left")
    df["revenue_usd"] = df["amount"] * df["rate_to_usd"]

    out = (
        df.groupby(["order_date", "region"], dropna=False)
        .agg(order_count=("order_id", "count"), revenue_usd=("revenue_usd", "sum"))
        .reset_index()
        .rename(columns={"order_date": "date"})
    )
    return out
