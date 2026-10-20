"""Runs the transform on the sample CSVs and prints the report."""
import pandas as pd

from transform import build_daily_revenue


def main():
    orders = pd.read_csv("data/orders.csv")
    customers = pd.read_csv("data/customers.csv")
    fx = pd.read_csv("data/fx_rates.csv")

    report = build_daily_revenue(orders, customers, fx)

    print(f"input orders (distinct ids): {orders['order_id'].nunique()}")
    print(f"report order_count total:    {report['order_count'].sum()}")
    print(f"report revenue_usd total:    {report['revenue_usd'].sum():.2f}")
    print()
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
