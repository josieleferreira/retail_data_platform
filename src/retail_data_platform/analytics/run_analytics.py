"""Coordena as análises descritivas e os artefatos de Analytics."""

from pathlib import Path
import json
import pandas as pd
from .sales_analysis import analyze_sales
from .customer_analysis import analyze_customers
from .product_analysis import analyze_products


def analyze(marts: dict[str, pd.DataFrame], output_dir: Path) -> dict:
    tables_dir = output_dir / "tables"
    charts_dir = output_dir / "charts"
    tables_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)
    sales = marts["mart_sales_items"].copy()
    sales["order_date"] = pd.to_datetime(sales.order_date)
    sales_result = analyze_sales(sales, marts["mart_daily_sales"], tables_dir, charts_dir)
    top_customers = analyze_customers(marts["mart_customer_360"], tables_dir, charts_dir)
    product_result = analyze_products(sales, marts["mart_product_performance"], tables_dir, charts_dir)
    metrics = sales_result["metrics"]
    metrics.update({
        "loss_item_rows": product_result["loss_item_rows"],
        "total_transaction_losses": product_result["total_transaction_losses"],
    })
    (output_dir / "business_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        **sales_result,
        "metrics": metrics,
        "losses": product_result["losses"],
        "top_customers": top_customers,
    }

