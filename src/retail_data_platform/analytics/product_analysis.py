"""Rentabilidade, prejuízos transacionais e desempenho de produtos."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from .visuals import COLORS, save_figure


def analyze_products(sales: pd.DataFrame, products: pd.DataFrame, tables_dir: Path, charts_dir: Path) -> dict:
    losses = (sales[sales.gross_profit < 0]
              .groupby(["product_id", "product_name"], as_index=False)
              .agg(loss_items=("order_item_id", "size"),
                   loss_amount=("gross_profit", lambda x: -x.sum()),
                   affected_revenue=("net_revenue", "sum"))
              .sort_values("loss_amount", ascending=False).head(15))
    losses.to_csv(tables_dir / "product_loss_ranking.csv", index=False)
    products.sort_values("gross_profit").head(15).to_csv(tables_dir / "lowest_accumulated_profit.csv", index=False)
    plot_data = losses.sort_values("loss_amount")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_data.product_name.str.slice(0, 36), plot_data.loss_amount / 1000, color=COLORS[4])
    ax.set(title="Prejuízo em transações por produto", xlabel="Prejuízo (R$ mil)", ylabel="")
    save_figure(fig, charts_dir / "product_losses.png")
    return {
        "losses": losses,
        "loss_item_rows": int((sales.gross_profit < 0).sum()),
        "total_transaction_losses": float(-sales.loc[sales.gross_profit < 0, "gross_profit"].sum()),
    }

