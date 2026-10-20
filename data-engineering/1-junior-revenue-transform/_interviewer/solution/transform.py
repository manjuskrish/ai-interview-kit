"""Builds the daily revenue report (reference solution)."""
import pandas as pd


def build_daily_revenue(orders: pd.DataFrame, customers: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    # 1. De-duplicate orders: keep the latest ingested version of each order.
    o = orders.copy()
    o["ingested_at"] = pd.to_datetime(o["ingested_at"], utc=True)
    o = o.sort_values(["order_id", "ingested_at"]).drop_duplicates("order_id", keep="last")

    # 2. Bucket by UTC date.
    created_utc = pd.to_datetime(o["created_at"], utc=True)
    o["date"] = created_utc.dt.strftime("%Y-%m-%d")

    # 3. One customer row per customer_id (the latest), so the join cannot fan out.
    c = customers.copy()
    c["updated_at"] = pd.to_datetime(c["updated_at"], utc=True)
    c = (
        c.sort_values(["customer_id", "updated_at"])
        .drop_duplicates("customer_id", keep="last")[["customer_id", "region"]]
    )
    df = o.merge(c, on="customer_id", how="left", validate="many_to_one")
    df["region"] = df["region"].fillna("UNKNOWN")

    # 4. FX: the latest rate on or before the order's UTC date, per currency.
    rates = fx.copy()
    rates["fx_date"] = pd.to_datetime(rates["date"]).astype("datetime64[ns]")
    rates = rates[["fx_date", "currency", "rate_to_usd"]].sort_values("fx_date")
    df["date_dt"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")
    df = df.sort_values("date_dt")
    df = pd.merge_asof(df, rates, left_on="date_dt", right_on="fx_date", by="currency", direction="backward")
    missing = df.loc[df["rate_to_usd"].isna(), "order_id"].tolist()
    if missing:
        raise ValueError(f"no FX rate available for orders: {missing}")

    df["revenue_usd"] = df["amount"] * df["rate_to_usd"]
    out = df.groupby(["date", "region"], as_index=False).agg(
        order_count=("order_id", "count"),
        revenue_usd=("revenue_usd", "sum"),
    )
    out["revenue_usd"] = out["revenue_usd"].round(2)
    return out.sort_values(["date", "region"]).reset_index(drop=True)
