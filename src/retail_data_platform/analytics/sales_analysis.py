"""Indicadores, sazonalidade e desempenho por canal."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from .visuals import COLORS, save_figure


def analyze_sales(sales: pd.DataFrame, daily: pd.DataFrame, tables_dir: Path, charts_dir: Path) -> dict:
    sales = sales.copy()
    daily = daily.copy()
    sales["order_date"] = pd.to_datetime(sales.order_date)
    daily["date"] = pd.to_datetime(daily.date)
    metrics = {
        "period_start": str(sales.order_date.min().date()),
        "period_end": str(sales.order_date.max().date()),
        "paid_orders": int(sales.order_id.nunique()),
        "active_customers": int(sales.customer_id.nunique()),
        "net_revenue": float(sales.net_revenue.sum()),
        "gross_profit": float(sales.gross_profit.sum()),
        "margin_pct": float(sales.gross_profit.sum() / sales.net_revenue.sum()),
        "refund_amount": float(sales.refund_amount.sum()),
        "avg_ticket": float(sales.groupby("order_id").net_revenue.sum().mean()),
    }
    metrics["refund_rate_pct"] = metrics["refund_amount"] / (metrics["net_revenue"] + metrics["refund_amount"])
    weekday_names = {
        0: "Domingo", 1: "Segunda-feira", 2: "Terça-feira",
        3: "Quarta-feira", 4: "Quinta-feira", 5: "Sexta-feira",
        6: "Sábado",
    }
    weekdays = (daily.assign(weekday_name=daily.weekday.map(weekday_names))
                .groupby(["weekday", "weekday_name"], as_index=False)
                .agg(avg_daily_sales=("net_revenue", "mean"), days=("date", "size"),
                     zero_sales_days=("orders", lambda x: int((x == 0).sum())))
                .sort_values("weekday"))
    monthly = (sales.assign(month=sales.order_date.dt.to_period("M").dt.to_timestamp())
               .groupby("month", as_index=False)
               .agg(net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"),
                    orders=("order_id", "nunique")))
    channel = sales.groupby("channel", as_index=False).agg(
        net_revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"))
    weekdays.to_csv(tables_dir / "average_sales_by_weekday.csv", index=False)
    monthly.to_csv(tables_dir / "monthly_sales.csv", index=False)
    channel.to_csv(tables_dir / "channel_performance.csv", index=False)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly.month, monthly.net_revenue / 1e6, color=COLORS[1], lw=2)
    ax.fill_between(monthly.month, monthly.net_revenue / 1e6, alpha=.12, color=COLORS[1])
    ax.set(title="Receita líquida mensal", ylabel="R$ milhões", xlabel="")
    save_figure(fig, charts_dir / "monthly_revenue.png")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(weekdays.weekday_name, weekdays.avg_daily_sales / 1000, color=COLORS[1])
    ax.set(title="Venda média por dia da semana (inclui dias sem venda)", ylabel="R$ mil/dia", xlabel="")
    ax.tick_params(axis="x", rotation=25)
    save_figure(fig, charts_dir / "weekday_sales.png")
    return {"metrics": metrics, "weekdays": weekdays, "monthly": monthly, "channel": channel}
