"""Manifesto de execução reproduzível, sem valores brutos ou caminhos locais."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any, Iterator
from uuid import uuid4
import json


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


class AuditRun:
    """Registra execução, etapas, fontes e artefatos com metadados mínimos."""

    def __init__(self, pipeline: str, output_root: Path, git_commit: str | None = None):
        self.run_id = str(uuid4())
        self.output_dir = output_root / self.run_id
        self.manifest_path = self.output_dir / "run_manifest.json"
        self._started_clock = perf_counter()
        self.manifest: dict[str, Any] = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "pipeline": pipeline,
            "status": "STARTED",
            "started_at": _utc_now(),
            "finished_at": None,
            "duration_seconds": None,
            "git_commit": git_commit,
            "steps": [],
            "sources": [],
            "datasets": [],
            "artifacts": [],
            "quality_gates": [],
            "error": None,
        }
        self._write()

    def _write(self) -> None:
        _atomic_json(self.manifest_path, self.manifest)

    @contextmanager
    def step(self, name: str) -> Iterator[None]:
        record = {"name": name, "status": "STARTED", "started_at": _utc_now()}
        started = perf_counter()
        self.manifest["steps"].append(record)
        self._write()
        try:
            yield
        except Exception as exc:
            record.update({
                "status": "FAILED",
                "finished_at": _utc_now(),
                "duration_seconds": round(perf_counter() - started, 6),
                "error_type": type(exc).__name__,
            })
            self._write()
            raise
        else:
            record.update({
                "status": "COMPLETED",
                "finished_at": _utc_now(),
                "duration_seconds": round(perf_counter() - started, 6),
            })
            self._write()

    def add_source(self, path: Path, row_count: int | None = None) -> None:
        self.manifest["sources"].append({
            "dataset": path.stem.lower(),
            "file_name": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "row_count": row_count,
        })

    def add_dataset(self, name: str, rows: int, columns: list[str]) -> None:
        schema = "|".join(columns).encode("utf-8")
        self.manifest["datasets"].append({
            "dataset": name,
            "row_count": rows,
            "column_count": len(columns),
            "schema_sha256": sha256(schema).hexdigest(),
        })

    def add_artifact(self, path: Path, relative_to: Path) -> None:
        resolved = path.resolve()
        root = relative_to.resolve()
        try:
            relative = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise ValueError("O artefato deve estar dentro da raiz informada") from exc
        self.manifest["artifacts"].append({
            "path": relative,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    def add_quality_gates(self, results: list[dict[str, Any]]) -> None:
        self.manifest["quality_gates"] = results
        self._write()

    def finish(self, status: str, error: Exception | None = None) -> None:
        if status not in {"COMPLETED", "FAILED"}:
            raise ValueError("Status final inválido")
        self.manifest.update({
            "status": status,
            "finished_at": _utc_now(),
            "duration_seconds": round(perf_counter() - self._started_clock, 6),
            "error": None if error is None else {"type": type(error).__name__},
        })
        self._write()

    def __enter__(self) -> "AuditRun":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.finish("FAILED" if exc else "COMPLETED", exc)
        return False
