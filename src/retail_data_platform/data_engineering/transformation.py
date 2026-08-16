from __future__ import annotations

from pathlib import Path
import pandas as pd

DATE_COLUMNS = {
    "created_at", "updated_at", "placed_at", "paid_at", "issued_at",
    "received_at", "occurred_at", "expected_delivery_at", "hire_date",
    "termination_date",
}
BOOL_COLUMNS = {"is_active", "is_primary", "is_preferred"}
INTEGER_COLUMNS = {
    "id", "customer_id", "brand_id", "category_id", "parent_category_id",
    "salesperson_id", "location_id", "order_id", "product_id",
    "product_variant_id", "supplier_id", "employee_id", "buyer_id",
    "destination_location_id", "received_by_employee_id", "purchase_order_id",
    "purchase_order_item_id", "goods_receipt_id", "return_id", "order_item_id",
    "exchange_variant_id", "attribute_id", "primary_location_id", "installments",
    "lead_time_days", "series",
}
DECIMAL_COLUMNS = {
    "subtotal", "discount_amount", "total", "amount", "unit_price", "line_total",
    "sale_price", "cost_price", "weight_kg", "icms_rate", "ipi_rate",
    "last_quoted_cost", "quantity_ordered", "unit_cost", "quantity_received",
    "quantity_on_hand", "reorder_point", "total_refund_amount",
    "unit_refund_amount", "quantity",
}


def read_and_clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=True, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()
        if col in DATE_COLUMNS:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif col in BOOL_COLUMNS:
            df[col] = df[col].str.upper().map({"TRUE": True, "FALSE": False}).astype("boolean")
        elif col in INTEGER_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif col in DECIMAL_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
    return df


def curate(files: list[Path]) -> dict[str, pd.DataFrame]:
    """Limpa e tipa as fontes somente em memória, sem duplicar os dados."""
    tables = {}
    for path in files:
        frame = read_and_clean(path)
        tables[path.stem] = frame
    return tables
