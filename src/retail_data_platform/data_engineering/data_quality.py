"""Auditoria de qualidade e integridade referencial."""

from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

PK = {
    "addresses": ["id"], "attributes": ["id"], "brands": ["id"], "categories": ["id"],
    "customers": ["id"], "employees": ["id"], "fiscal_invoices": ["id"],
    "goods_receipt_items": ["id"], "goods_receipts": ["id"], "locations": ["id"],
    "order_items": ["id"], "orders": ["id"], "payments": ["id"],
    "product_suppliers": ["product_variant_id", "supplier_id"], "product_variants": ["id"],
    "products": ["id"], "purchase_order_items": ["id"], "purchase_orders": ["id"],
    "return_items": ["id"], "returns": ["id"],
    "stock_levels": ["product_variant_id", "location_id"], "stock_movements": ["id"],
    "suppliers": ["id"], "variant_attribute_values": ["product_variant_id", "attribute_id"],
}

FKS = [
    ("addresses", "customer_id", "customers", "id"), ("orders", "customer_id", "customers", "id"),
    ("orders", "salesperson_id", "employees", "id"), ("orders", "location_id", "locations", "id"),
    ("order_items", "order_id", "orders", "id"),
    ("order_items", "product_variant_id", "product_variants", "id"),
    ("product_variants", "product_id", "products", "id"),
    ("products", "brand_id", "brands", "id"), ("products", "category_id", "categories", "id"),
    ("payments", "order_id", "orders", "id"), ("fiscal_invoices", "order_id", "orders", "id"),
    ("returns", "order_id", "orders", "id"), ("return_items", "return_id", "returns", "id"),
    ("return_items", "order_item_id", "order_items", "id"),
    ("purchase_order_items", "purchase_order_id", "purchase_orders", "id"),
    ("purchase_order_items", "product_variant_id", "product_variants", "id"),
    ("stock_levels", "product_variant_id", "product_variants", "id"),
    ("stock_levels", "location_id", "locations", "id"),
    ("stock_movements", "product_variant_id", "product_variants", "id"),
    ("stock_movements", "location_id", "locations", "id"),
]


def audit(tables: dict[str, pd.DataFrame], output: Path) -> dict:
    report = {"summary": {}, "tables": {}, "foreign_keys": [], "checks": {}}
    for name, df in sorted(tables.items()):
        report["tables"][name] = {
            "rows": len(df), "columns": len(df.columns),
            "duplicate_primary_key": int(df.duplicated(PK[name]).sum()),
            "null_cells": int(df.isna().sum().sum()),
        }
    for child, col, parent, pcol in FKS:
        values = tables[child][col].dropna()
        orphans = int((~values.isin(tables[parent][pcol])).sum())
        report["foreign_keys"].append({"relationship": f"{child}.{col}->{parent}.{pcol}", "orphans": orphans})
    o, i = tables["orders"], tables["order_items"]
    report["checks"] = {
        "order_amount_mismatches": int(((o.subtotal - o.discount_amount - o.total).abs() > 0.011).sum()),
        "item_amount_mismatches": int(((i.quantity * i.unit_price - i.line_total).abs() > 0.011).sum()),
        "missing_reorder_point_pct": round(100 * tables["stock_levels"].reorder_point.isna().mean(), 2),
        "min_order_date": str(o.placed_at.min()), "max_order_date": str(o.placed_at.max()),
    }
    report["summary"] = {
        "tables": len(tables), "rows": sum(len(x) for x in tables.values()),
        "duplicate_primary_keys": sum(x["duplicate_primary_key"] for x in report["tables"].values()),
        "foreign_key_orphans": sum(x["orphans"] for x in report["foreign_keys"]),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
