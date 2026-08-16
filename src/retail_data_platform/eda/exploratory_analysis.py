"""Gera evidências independentes de EDA antes das regras analíticas."""

from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def analyze_eda(tables: dict[str, pd.DataFrame], output_dir: Path) -> dict:
    tables_dir = output_dir / "tables"
    charts_dir = output_dir / "charts"
    tables_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    inventory_rows = []
    missing_rows = []
    for name, frame in sorted(tables.items()):
        inventory_rows.append({
            "table": name,
            "rows": len(frame),
            "columns": len(frame.columns),
            "missing_cells": int(frame.isna().sum().sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
        })
        for column, count in frame.isna().sum().items():
            if count:
                missing_rows.append({
                    "table": name,
                    "column": column,
                    "missing_count": int(count),
                    "missing_pct": float(count / len(frame)),
                })
    inventory = pd.DataFrame(inventory_rows)
    missing = pd.DataFrame(missing_rows).sort_values("missing_pct", ascending=False)
    inventory.to_csv(tables_dir / "table_inventory.csv", index=False)
    missing.to_csv(tables_dir / "missing_values.csv", index=False)

    orders = tables["orders"].copy()
    orders["placed_at"] = pd.to_datetime(orders.placed_at)
    status = orders.status.value_counts().rename_axis("status").reset_index(name="orders")
    channels = orders.channel.value_counts().rename_axis("channel").reset_index(name="orders")
    status.to_csv(tables_dir / "order_status_distribution.csv", index=False)
    channels.to_csv(tables_dir / "order_channel_distribution.csv", index=False)

    numeric_frames = []
    candidates = {
        "orders": ["subtotal", "discount_amount", "total"],
        "order_items": ["quantity", "unit_price", "line_total"],
        "product_variants": ["sale_price", "cost_price", "weight_kg"],
        "stock_levels": ["quantity_on_hand", "reorder_point"],
        "returns": ["total_refund_amount"],
    }
    for table, columns in candidates.items():
        for column in columns:
            series = pd.to_numeric(tables[table][column], errors="coerce")
            desc = series.describe(percentiles=[.25, .5, .75, .95]).to_dict()
            numeric_frames.append({"table": table, "column": column, **desc})
    numeric_summary = pd.DataFrame(numeric_frames)
    numeric_summary.to_csv(tables_dir / "numeric_summary.csv", index=False)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(status.status, status.orders, color="#1367a8")
    ax.set(title="Distribuição dos pedidos por status", xlabel="Status", ylabel="Pedidos")
    _save(fig, charts_dir / "orders_by_status.png")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(channels.channel, channels.orders, color=["#19a7a0", "#f2b134"])
    ax.set(title="Distribuição dos pedidos por canal", xlabel="Canal", ylabel="Pedidos")
    _save(fig, charts_dir / "orders_by_channel.png")

    paid = orders.loc[orders.status == "paid", "total"].astype(float)
    upper = paid.quantile(.99)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(paid[paid <= upper], bins=40, color="#0b1f5e", alpha=.85)
    ax.set(title="Distribuição do valor de pedidos pagos (até P99)", xlabel="Valor do pedido (R$)", ylabel="Frequência")
    _save(fig, charts_dir / "paid_order_value_distribution.png")

    total_rows = int(inventory.rows.sum())
    report = f"""# EDA — Análise Exploratória de Dados

## Escopo

Foram examinadas **{len(tables)} tabelas**, totalizando **{total_rows:,} registros**. A janela dos pedidos vai de **{orders.placed_at.min()}** a **{orders.placed_at.max()}**.

## Estrutura e integridade inicial

- Inventário completo: `tables/table_inventory.csv`.
- Ausência por coluna: `tables/missing_values.csv`.
- Estatísticas numéricas: `tables/numeric_summary.csv`.
- Distribuições de status e canal: arquivos específicos em `tables/` e `charts/`.
- Duplicidades de linha completas encontradas: **{int(inventory.duplicate_rows.sum()):,}**.

## Principais observações

- Pedidos pagos: **{int((orders.status == 'paid').sum()):,}**.
- Pedidos cancelados: **{int((orders.status == 'cancelled').sum()):,}**.
- O campo `stock_levels.reorder_point` está totalmente ausente e não deve ser imputado sem uma política de estoque definida.
- A ausência de vendedor em pedidos de e-commerce é compatível com o processo operacional e não é tratada como erro.
- Campos opcionais, como complemento de endereço e data de desligamento, permanecem nulos para preservar seu significado.

## Decisões decorrentes da EDA

1. Reconhecer receita somente para pedidos pagos.
2. Separar ausência estrutural de problema de qualidade.
3. Preservar dias sem venda na análise semanal.
4. Usar validação temporal na previsão para evitar vazamento de dados futuros.
5. Não automatizar reposição enquanto o ponto de reposição não estiver definido.
"""
    (output_dir / "EDA_REPORT.md").write_text(report, encoding="utf-8")
    return {"tables": len(tables), "rows": total_rows, "inventory": inventory, "missing": missing}

