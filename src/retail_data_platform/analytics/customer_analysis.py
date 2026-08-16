"""Análise de valor e lucratividade de clientes."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from .visuals import COLORS, save_figure


def analyze_customers(customers: pd.DataFrame, tables_dir: Path, charts_dir: Path) -> pd.DataFrame:
    top_customers = customers.nlargest(15, "gross_profit").copy()
    top_customers.insert(0, "customer_label", [f"Cliente {rank:02d}" for rank in range(1, len(top_customers) + 1)])
    public_columns = [
        "customer_label", "first_purchase_date", "last_purchase_date", "paid_orders",
        "units", "net_revenue", "gross_profit", "avg_ticket", "refunded_amount",
    ]
    top_customers = top_customers[public_columns]
    top_customers.to_csv(tables_dir / "top_customers_by_profit.csv", index=False)
    plot_data = top_customers.sort_values("gross_profit")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_data.customer_label, plot_data.gross_profit / 1000, color=COLORS[2])
    ax.set(title="Clientes com maior lucro acumulado", xlabel="Lucro bruto (R$ mil)", ylabel="")
    save_figure(fig, charts_dir / "top_customers.png")
    return top_customers
