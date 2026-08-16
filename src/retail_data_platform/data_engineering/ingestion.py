"""Extração segura das fontes sem alteração dos arquivos originais."""

from __future__ import annotations

from pathlib import Path
import shutil
import zipfile


def extract_source(source: Path, raw_dir: Path) -> list[Path]:
    if not source.exists():
        raise FileNotFoundError(f"Fonte não encontrada: {source}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        if source.resolve() != raw_dir.resolve():
            for path in source.glob("*.csv"):
                shutil.copy2(path, raw_dir / path.name)
    elif zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            unsafe = [name for name in archive.namelist() if ".." in Path(name).parts or Path(name).is_absolute()]
            if unsafe:
                raise ValueError(f"ZIP contém caminhos inseguros: {unsafe[:3]}")
            archive.extractall(raw_dir)
    else:
        raise ValueError("A fonte deve ser uma pasta de CSVs ou um arquivo ZIP")
    files = sorted(raw_dir.rglob("*.csv"))
    if len(files) != 24:
        raise ValueError(f"Esperados 24 CSVs, encontrados {len(files)}")
    return files
