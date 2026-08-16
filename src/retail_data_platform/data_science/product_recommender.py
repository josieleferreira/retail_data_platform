"""Recomendação item-a-item baseada em cestas pagas."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def recommend(sales: pd.DataFrame, output_dir: Path, top_k=5) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    baskets = sales[["order_id", "product_id", "product_name"]].drop_duplicates()
    pairs = baskets.merge(baskets, on="order_id", suffixes=("_a", "_b"))
    pairs = pairs[pairs.product_id_a < pairs.product_id_b]
    pair_counts = pairs.groupby(["product_id_a", "product_name_a", "product_id_b", "product_name_b"], as_index=False).order_id.nunique().rename(columns={"order_id":"pair_orders"})
    counts = baskets.groupby(["product_id", "product_name"]).order_id.nunique().rename("product_orders").reset_index()
    total_orders = baskets.order_id.nunique()
    pair_counts = pair_counts.merge(counts.rename(columns={"product_id":"product_id_a","product_name":"product_name_a","product_orders":"orders_a"}), on=["product_id_a","product_name_a"])
    pair_counts = pair_counts.merge(counts.rename(columns={"product_id":"product_id_b","product_name":"product_name_b","product_orders":"orders_b"}), on=["product_id_b","product_name_b"])
    ab = pair_counts.rename(columns={"product_id_a":"source_product_id","product_name_a":"source_product_name","product_id_b":"recommended_product_id","product_name_b":"recommended_product_name","orders_a":"source_orders","orders_b":"recommended_orders"})
    ba = pair_counts.rename(columns={"product_id_b":"source_product_id","product_name_b":"source_product_name","product_id_a":"recommended_product_id","product_name_a":"recommended_product_name","orders_b":"source_orders","orders_a":"recommended_orders"})
    out = pd.concat([ab, ba], ignore_index=True)
    out["confidence"] = out.pair_orders / out.source_orders
    out["lift"] = out.confidence / (out.recommended_orders / total_orders)
    out["support"] = out.pair_orders / total_orders
    out = out.sort_values(["source_product_id", "lift", "pair_orders"], ascending=[True, False, False])
    out = out.groupby("source_product_id", group_keys=False).head(top_k)
    cols = ["source_product_id","source_product_name","recommended_product_id","recommended_product_name","pair_orders","confidence","lift","support"]
    out[cols].to_csv(output_dir / "product_recommendations.csv", index=False)
    return out[cols]
