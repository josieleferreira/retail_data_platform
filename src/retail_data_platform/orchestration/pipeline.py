"""Orquestra o fluxo completo com auditoria, gates e linhagem."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os

from ..data_engineering.ingestion import extract_source
from ..data_engineering.transformation import curate
from ..data_engineering.data_quality import audit
from ..data_engineering.dbt_warehouse import build_marts_with_dbt
from ..eda.exploratory_analysis import analyze_eda
from ..analytics.run_analytics import analyze
from ..analytics.reporting import build_report
from ..data_science.demand_forecasting import forecast
from ..data_science.product_recommender import recommend
from ..governance.audit import AuditRun
from ..governance.catalog import validate_catalog
from ..governance.lineage import build_lineage, write_openlineage_event
from ..governance.quality_gates import QualityGateError, evaluate_quality_gates
from .presentation import organize_deliverables


def run(source: Path, root: Path) -> None:
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    raw_dir = root / "data" / "raw"
    audit_root = root / "artifacts" / "runtime" / "audit"
    lineage_root = root / "artifacts" / "runtime" / "lineage"

    with AuditRun("retail_data_platform.full_pipeline", audit_root, os.getenv("GITHUB_SHA")) as audit_run:
        print("[1/11] Validando catálogo e classificações...")
        with audit_run.step("catalog_validation"):
            validate_catalog(
                root / "metadata" / "datasets.json",
                root / "metadata" / "classifications.json",
            )

        print("[2/11] Localizando fontes raw...")
        with audit_run.step("source_ingestion"):
            files = extract_source(source, raw_dir)

        print("[3/11] Limpando e tipando em memória...")
        with audit_run.step("in_memory_curation"):
            tables = curate(files)
            for path in sorted(files):
                audit_run.add_source(path, len(tables[path.stem.lower()]))
            for name, table in sorted(tables.items()):
                audit_run.add_dataset(f"raw.{name}", len(table), list(table.columns))

        print("[4/11] Gerando EDA independente...")
        with audit_run.step("exploratory_analysis"):
            analyze_eda(tables, root / "deliverables" / "01_EDA")

        with TemporaryDirectory(prefix="retail_data_runtime_") as temporary:
            runtime = Path(temporary)
            engineering_dir = runtime / "engineering"
            analytics_dir = runtime / "analytics"
            forecasting_dir = runtime / "data_science" / "forecasting"
            recommendations_dir = runtime / "data_science" / "recommendations"

            print("[5/11] Auditando qualidade e aplicando gates...")
            with audit_run.step("data_quality"):
                quality = audit(tables, engineering_dir / "data_quality_report.json")
                try:
                    gate_results = evaluate_quality_gates(
                        quality, root / "metadata" / "quality_rules.json"
                    )
                except QualityGateError as error:
                    audit_run.add_quality_gates(error.results)
                    raise
                audit_run.add_quality_gates(gate_results)

            print("[6/11] Construindo e testando marts com dbt + DuckDB...")
            with audit_run.step("dbt_build_and_test"):
                dbt_artifact_dir = root / "artifacts" / "runtime" / "dbt" / audit_run.run_id
                marts = build_marts_with_dbt(
                    tables, root / "dbt", runtime / "dbt", dbt_artifact_dir
                )
                for name, table in sorted(marts.items()):
                    audit_run.add_dataset(
                        name.replace("mart_", "mart."), len(table), list(table.columns)
                    )
                for path in sorted(dbt_artifact_dir.rglob("*")):
                    if path.is_file():
                        audit_run.add_artifact(path, root)

            print("[7/11] Gerando análises de negócio...")
            with audit_run.step("business_analytics"):
                analysis = analyze(marts, analytics_dir)

            print("[8/11] Treinando previsão e recomendações...")
            with audit_run.step("data_science"):
                forecast_result = forecast(
                    marts["mart_sales_items"], forecasting_dir, forecasting_dir / "model",
                    config["forecast_top_products"], config["forecast_horizon_months"],
                    config["forecast_test_months"], config["random_seed"],
                )
                recommendations = recommend(
                    marts["mart_sales_items"], recommendations_dir,
                    config["recommendations_per_product"],
                )

            print("[9/11] Construindo dashboard...")
            with audit_run.step("dashboard_generation"):
                build_report(analysis, forecast_result, recommendations, quality, analytics_dir)

            print("[10/11] Organizando entregas...")
            with audit_run.step("delivery_publishing"):
                organize_deliverables(
                    root, runtime, analysis, forecast_result, recommendations, quality
                )
                for path in sorted((root / "deliverables").rglob("*")):
                    if path.is_file():
                        audit_run.add_artifact(path, root)

        print("[11/11] Gerando linhagem técnica...")
        with audit_run.step("lineage_generation"):
            lineage_path = lineage_root / f"{audit_run.run_id}.json"
            lineage = build_lineage(
                root / "metadata" / "lineage.json", lineage_path, audit_run.run_id
            )
            inputs = sorted({edge["input"] for edge in lineage["edges"]})
            outputs = sorted({edge["output"] for edge in lineage["edges"]})
            openlineage_path = lineage_root / f"{audit_run.run_id}.openlineage.json"
            write_openlineage_event(
                openlineage_path, audit_run.run_id, lineage["job"], inputs, outputs
            )
            audit_run.add_artifact(lineage_path, root)
            audit_run.add_artifact(lineage_path.with_suffix(".mmd"), root)
            audit_run.add_artifact(openlineage_path, root)

    print(f"Concluído: {root / 'deliverables'}")
