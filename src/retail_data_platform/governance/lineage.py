"""Geração e validação de linhagem declarada e eventos OpenLineage."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_lineage(spec_path: Path, output_path: Path, run_id: str) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    outputs = {edge["output"] for edge in spec["edges"]}
    missing = sorted(set(spec["required_outputs"]) - outputs)
    if missing:
        raise ValueError("Saídas sem upstream declarado: " + ", ".join(missing))
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": _utc_now(),
        "job": spec["job"],
        "edges": spec["edges"],
        "column_lineage": spec["column_lineage"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    mermaid = ["flowchart LR"]
    for edge in spec["edges"]:
        source = edge["input"].replace(".", "_").replace("/", "_")
        target = edge["output"].replace(".", "_").replace("/", "_")
        mermaid.append(f'    {source}["{edge["input"]}"] --> {target}["{edge["output"]}"]')
    output_path.with_suffix(".mmd").write_text("\n".join(mermaid) + "\n", encoding="utf-8")
    return payload


def write_openlineage_event(
    output_path: Path,
    run_id: str,
    job_name: str,
    inputs: list[str],
    outputs: list[str],
    event_type: str = "COMPLETE",
) -> dict[str, Any]:
    if event_type not in {"START", "COMPLETE", "FAIL"}:
        raise ValueError("Tipo de evento OpenLineage inválido")
    event = {
        "eventType": event_type,
        "eventTime": _utc_now(),
        "producer": "https://github.com/josieleferreira/retail_data_platform",
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
        "run": {"runId": run_id},
        "job": {"namespace": "retail-data-platform", "name": job_name},
        "inputs": [{"namespace": "retail-data-platform", "name": name} for name in inputs],
        "outputs": [{"namespace": "retail-data-platform", "name": name} for name in outputs],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    return event
