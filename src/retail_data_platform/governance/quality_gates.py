"""Quality gates configuráveis para interromper cargas com falhas críticas."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import operator


class QualityGateError(RuntimeError):
    """Indica falha em uma regra de qualidade classificada como ERROR."""

    def __init__(self, message: str, results: list[dict[str, Any]]):
        super().__init__(message)
        self.results = results


OPERATORS = {
    "eq": operator.eq,
    "lte": operator.le,
    "gte": operator.ge,
}


def _resolve(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        current = current[part]
    return current


def evaluate_quality_gates(report: dict[str, Any], rules_path: Path) -> list[dict[str, Any]]:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))["rules"]
    results: list[dict[str, Any]] = []
    for rule in rules:
        operation = OPERATORS[rule["operator"]]
        observed = _resolve(report, rule["metric"])
        passed = bool(operation(observed, rule["threshold"]))
        results.append({
            "rule_id": rule["id"],
            "description": rule["description"],
            "severity": rule["severity"],
            "metric": rule["metric"],
            "operator": rule["operator"],
            "threshold": rule["threshold"],
            "observed": observed,
            "passed": passed,
        })
    failed = [result["rule_id"] for result in results if not result["passed"] and result["severity"] == "ERROR"]
    if failed:
        raise QualityGateError("Quality gates críticos reprovados: " + ", ".join(failed), results)
    return results
