"""Orquestra o fluxo completo mantendo somente as fontes raw em disco."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json

from ..data_engineering.ingestion import extract_source
from ..data_engineering.transformation import curate
from ..data_engineering.data_quality import audit
from ..data_engineering.warehouse import build_marts_in_memory
from ..eda.exploratory_analysis import analyze_eda
from ..analytics.run_analytics import analyze
from ..analytics.reporting import build_report
from ..data_science.demand_forecasting import forecast
from ..data_science.product_recommender import recommend
from .presentation import organize_deliverables


def run(source: Path, root: Path) -> None:
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    raw_dir = root / "data" / "raw"
    print("[1/9] Localizando fontes raw...")
    files = extract_source(source, raw_dir)
    print("[2/9] Limpando e tipando em memória...")
    tables = curate(files)
    print("[3/9] Gerando EDA independente...")
    analyze_eda(tables, root / "deliverables" / "01_EDA")

    with TemporaryDirectory(prefix="retail_data_runtime_") as temporary:
        runtime = Path(temporary)
        engineering_dir = runtime / "engineering"
        analytics_dir = runtime / "analytics"
        forecasting_dir = runtime / "data_science" / "forecasting"
        recommendations_dir = runtime / "data_science" / "recommendations"
        print("[4/9] Auditando qualidade...")
        quality = audit(tables, engineering_dir / "data_quality_report.json")
        print("[5/9] Construindo marts SQL em memória...")
        marts = build_marts_in_memory(tables, root / "sql")
        print("[6/9] Gerando análises de negócio...")
        analysis = analyze(marts, analytics_dir)
        print("[7/9] Treinando previsão e recomendações...")
        forecast_result = forecast(
            marts["mart_sales_items"], forecasting_dir, forecasting_dir / "model",
            config["forecast_top_products"], config["forecast_horizon_months"],
            config["forecast_test_months"], config["random_seed"],
        )
        recommendations = recommend(
            marts["mart_sales_items"], recommendations_dir,
            config["recommendations_per_product"],
        )
        print("[8/9] Construindo dashboard...")
        build_report(analysis, forecast_result, recommendations, quality, analytics_dir)
        print("[9/9] Organizando entregas e linhagem...")
        organize_deliverables(
            root, runtime, analysis, forecast_result, recommendations, quality
        )
    print(f"Concluído: {root / 'deliverables'}")
