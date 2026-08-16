"""Organiza os resultados técnicos e analíticos do projeto."""

from __future__ import annotations

from pathlib import Path
import shutil
import pandas as pd


def _copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _brl(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%".replace(".", ",")


def organize_deliverables(root: Path, runtime: Path, analysis: dict, forecast: dict, recs: pd.DataFrame, quality: dict) -> None:
    delivery = root / "deliverables"
    eda_dir = delivery / "01_EDA"
    treatment_dir = delivery / "02_TRATAMENTO_DE_DADOS"
    sales_dir = delivery / "03_ANALISE_DE_VENDAS"
    customers_dir = delivery / "04_ANALISE_DE_CLIENTES"
    demand_dir = delivery / "05_PREVISAO_DE_DEMANDAS"
    recommendations_dir = delivery / "06_SISTEMAS_DE_RECOMENDACOES"
    for path in (eda_dir, treatment_dir, sales_dir, customers_dir, demand_dir, recommendations_dir):
        path.mkdir(parents=True, exist_ok=True)

    engineering = runtime / "engineering"
    analytics = runtime / "analytics"
    science = runtime / "data_science"
    _copy(engineering / "data_quality_report.json", treatment_dir / "data_quality_report.json")
    _copy(root / "docs" / "BUSINESS_RULES.md", treatment_dir / "BUSINESS_RULES.md")
    _copy(root / "docs" / "DATA_DICTIONARY.md", treatment_dir / "DATA_DICTIONARY.md")
    _copy(analytics / "tables" / "monthly_sales.csv", sales_dir / "monthly_sales.csv")
    _copy(analytics / "tables" / "channel_performance.csv", sales_dir / "channel_performance.csv")
    _copy(analytics / "tables" / "product_loss_ranking.csv", sales_dir / "product_loss_ranking.csv")
    _copy(analytics / "charts" / "monthly_revenue.png", sales_dir / "monthly_revenue.png")
    _copy(analytics / "charts" / "product_losses.png", sales_dir / "product_losses.png")
    _copy(analytics / "charts" / "weekday_sales.png", sales_dir / "weekday_sales.png")
    _copy(analytics / "tables" / "average_sales_by_weekday.csv", sales_dir / "average_sales_by_weekday.csv")
    _copy(analytics / "tables" / "top_customers_by_profit.csv", customers_dir / "top_customers_by_profit.csv")
    _copy(analytics / "charts" / "top_customers.png", customers_dir / "top_customers.png")
    for name in ("forecast_metrics.json", "forecast_backtest.csv", "demand_forecast_3_months.csv"):
        _copy(science / "forecasting" / name, demand_dir / name)
    _copy(science / "recommendations" / "product_recommendations.csv", recommendations_dir / "product_recommendations.csv")
    _copy(analytics / "dashboard_executivo.html", delivery / "DASHBOARD_EXECUTIVO.html")

    source_map = {
        eda_dir: sorted(path.name for path in (root / "data" / "raw").glob("*.csv")),
        treatment_dir: sorted(path.name for path in (root / "data" / "raw").glob("*.csv")),
        sales_dir: [
            "orders.csv", "order_items.csv", "product_variants.csv", "products.csv",
            "categories.csv", "brands.csv", "returns.csv", "return_items.csv",
        ],
        customers_dir: [
            "customers.csv", "orders.csv", "order_items.csv", "product_variants.csv",
            "products.csv", "returns.csv", "return_items.csv",
        ],
        demand_dir: [
            "orders.csv", "order_items.csv", "product_variants.csv", "products.csv",
            "returns.csv", "return_items.csv",
        ],
        recommendations_dir: [
            "orders.csv", "order_items.csv", "product_variants.csv", "products.csv",
        ],
    }
    lineage_sections = ["# Linhagem das bases por análise", "", "As fontes persistidas existem somente em `data/raw/`.", ""]
    for folder, names in source_map.items():
        lines = ["# Bases utilizadas", "", "Esta análise utiliza diretamente as seguintes fontes:", ""]
        lines.extend(f"- `../../data/raw/{name}`" for name in names)
        lines.extend(["", "As transformações e os marts SQL são construídos apenas em memória durante a execução.", ""])
        (folder / "DATA_SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
        lineage_sections.extend([f"## {folder.name}", ""])
        lineage_sections.extend(f"- `data/raw/{name}`" for name in names)
        lineage_sections.append("")
    (delivery / "DATA_LINEAGE.md").write_text("\n".join(lineage_sections), encoding="utf-8")

    m = analysis["metrics"]
    best_day = analysis["weekdays"].nlargest(1, "avg_daily_sales").iloc[0]
    top_loss = analysis["losses"].iloc[0]
    top_customer = analysis["top_customers"].iloc[0]
    readmes = {
        treatment_dir: """# Tratamento de dados\n\nEsta frente contém o relatório de qualidade, regras de negócio e dicionário dos marts. O código correspondente está em `src/retail_data_platform/data_engineering/` e o SQL em `sql/`. Os dados tratados e os marts existem apenas em memória.\n""",
        sales_dir: f"""# Análise de vendas\n\nReceita líquida: **{_brl(m['net_revenue'])}**. Lucro bruto: **{_brl(m['gross_profit'])}**. Margem: **{_pct(m['margin_pct'])}**. Inclui série mensal, canais, prejuízos e média semanal com dias sem venda.\n""",
        customers_dir: f"""# Análise de clientes\n\nO ranking usa lucro acumulado. O primeiro colocado é **{top_customer.customer_label}**, com **{_brl(top_customer.gross_profit)}** de lucro bruto estimado. Os rótulos foram anonimizados para publicação.\n""",
        demand_dir: f"""# Previsão de demandas\n\nO backtest temporal obteve WAPE de **{_pct(forecast['metrics']['wape_model'])}**, contra **{_pct(forecast['metrics']['wape_seasonal_naive'])}** do baseline sazonal. A pasta contém avaliação e previsão de três meses.\n""",
        recommendations_dir: """# Sistemas de recomendações\n\nRecomendações item-a-item baseadas em cestas pagas. O arquivo apresenta produto de origem, recomendado, pedidos conjuntos, confiança, lift e suporte.\n""",
    }
    for folder, content in readmes.items():
        (folder / "README.md").write_text(content, encoding="utf-8")

    responses = f"""# Síntese técnica e analítica

Este documento reúne os principais resultados da plataforma de dados para varejo multicanal.

## EDA

Foram avaliadas {quality['summary']['tables']} tabelas e {quality['summary']['rows']:,} registros. Não foram encontradas chaves primárias duplicadas nem registros órfãos nas relações verificadas. A exploração identificou ausência total do ponto de reposição e confirmou a necessidade de diferenciar nulos estruturais de falhas de qualidade. Evidências completas: `01_EDA/`.

## Tratamento de dados

Os 24 CSVs permanecem exclusivamente em `data/raw/`. Eles são tipados em memória e carregados em um SQLite temporário somente durante a execução. Os marts de vendas por item, cliente 360, desempenho de produtos e calendário diário não são persistidos. Pedidos pagos reconhecem receita; somente reembolsos concluídos são deduzidos.

## Análise geral de vendas

No período de {m['period_start']} a {m['period_end']}, {m['paid_orders']:,} pedidos pagos geraram {_brl(m['net_revenue'])} de receita líquida e {_brl(m['gross_profit'])} de lucro bruto estimado, com margem de {_pct(m['margin_pct'])}.

## Rentabilidade de produtos

Foram identificadas {m['loss_item_rows']} linhas de pedido com margem negativa, somando {_brl(m['total_transaction_losses'])}. O maior prejuízo transacional por produto foi **{top_loss.product_name}**, com {_brl(top_loss.loss_amount)}. Arquivo: `03_ANALISE_DE_VENDAS/product_loss_ranking.csv`.

## Clientes com maior lucro acumulado

O cliente de maior lucro foi **{top_customer.customer_label}**, com {_brl(top_customer.gross_profit)} em {int(top_customer.paid_orders)} pedidos pagos. Os clientes foram anonimizados no material público. O ranking completo está em `04_ANALISE_DE_CLIENTES/top_customers_by_profit.csv`.

## Vendas médias por dia da semana

Todos os dias civis entre a primeira e a última venda foram materializados; dias sem venda receberam zero antes do cálculo. **{best_day.weekday_name}** apresentou a maior média, {_brl(best_day.avg_daily_sales)} por dia. Evidências: `03_ANALISE_DE_VENDAS/average_sales_by_weekday.csv` e `weekday_sales.png`.

## Previsão de demandas

O modelo global cobre os 50 produtos de maior giro, usa defasagens e médias móveis e foi validado nos seis meses finais. WAPE do modelo: {_pct(forecast['metrics']['wape_model'])}; baseline sazonal: {_pct(forecast['metrics']['wape_seasonal_naive'])}. O horizonte entregue é de três meses.

## Sistemas de recomendações

O sistema usa coocorrência em pedidos pagos e ranqueia complementos por lift. Confiança, suporte e número de pedidos conjuntos acompanham cada recomendação para permitir auditoria e definição de corte mínimo.

## Material complementar

O dashboard consolidado está em `DASHBOARD_EXECUTIVO.html`.

A relação entre cada análise e suas fontes está em `DATA_LINEAGE.md` e nos arquivos `DATA_SOURCES.md` de cada frente.
"""
    (delivery / "PROJECT_SUMMARY.md").write_text(responses, encoding="utf-8")
