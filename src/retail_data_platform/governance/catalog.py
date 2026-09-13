"""Validação do catálogo de dados e das classificações de segurança."""

from __future__ import annotations

from pathlib import Path
import json


class CatalogValidationError(ValueError):
    """Indica catálogo incompleto ou classificação inválida."""


REQUIRED_FIELDS = {
    "name", "layer", "domain", "owner_role", "steward_role",
    "classification", "contains_pii", "retention_days", "sla",
}


def validate_catalog(catalog_path: Path, classifications_path: Path) -> list[dict]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    classifications = json.loads(classifications_path.read_text(encoding="utf-8"))
    allowed = set(classifications["classifications"])
    errors: list[str] = []
    names: set[str] = set()
    for dataset in catalog["datasets"]:
        missing = REQUIRED_FIELDS - set(dataset)
        if missing:
            errors.append(f"{dataset.get('name', '<sem nome>')}: campos ausentes {sorted(missing)}")
        name = dataset.get("name")
        if name in names:
            errors.append(f"dataset duplicado: {name}")
        names.add(name)
        if dataset.get("classification") not in allowed:
            errors.append(f"{name}: classificação inválida")
        if dataset.get("layer") == "public" and dataset.get("contains_pii") is not False:
            errors.append(f"{name}: saída pública não pode conter PII")
        if not isinstance(dataset.get("retention_days"), int) or dataset.get("retention_days", 0) <= 0:
            errors.append(f"{name}: retenção inválida")
    if errors:
        raise CatalogValidationError("; ".join(errors))
    return catalog["datasets"]
