"""Extração segura das fontes sem alteração dos arquivos originais."""

from __future__ import annotations

from pathlib import Path
import csv
import shutil
import zipfile


REQUIRED_COLUMNS = {
    "addresses": {"id", "customer_id"},
    "attributes": {"id"},
    "brands": {"id", "name"},
    "categories": {"id", "name"},
    "customers": {"id", "legal_name", "person_type"},
    "employees": {"id"},
    "fiscal_invoices": {"id", "order_id"},
    "goods_receipt_items": {"id", "goods_receipt_id", "purchase_order_item_id"},
    "goods_receipts": {"id", "purchase_order_id", "received_by_employee_id"},
    "locations": {"id"},
    "order_items": {"id", "order_id", "product_variant_id", "quantity", "unit_price", "line_total"},
    "orders": {
        "id", "order_number", "channel", "customer_id", "salesperson_id",
        "location_id", "status", "subtotal", "discount_amount", "total", "placed_at",
    },
    "payments": {"id", "order_id"},
    "product_suppliers": {"product_variant_id", "supplier_id"},
    "product_variants": {"id", "product_id", "cost_price"},
    "products": {"id", "name", "brand_id", "category_id"},
    "purchase_order_items": {"id", "purchase_order_id", "product_variant_id"},
    "purchase_orders": {"id", "supplier_id", "buyer_id", "destination_location_id"},
    "return_items": {"id", "return_id", "order_item_id", "quantity", "action", "unit_refund_amount"},
    "returns": {"id", "order_id", "status", "total_refund_amount"},
    "stock_levels": {"product_variant_id", "location_id", "reorder_point"},
    "stock_movements": {"id", "product_variant_id", "location_id"},
    "suppliers": {"id"},
    "variant_attribute_values": {"product_variant_id", "attribute_id"},
}


class SourceContractError(ValueError):
    """Indica que nomes ou colunas das fontes não atendem ao contrato."""


def validate_source_contract(files: list[Path]) -> list[Path]:
    """Valida nomes únicos e colunas mínimas antes de carregar os dados."""
    by_table: dict[str, Path] = {}
    duplicate_names: list[str] = []
    for path in files:
        table = path.stem.strip().lower()
        if table in by_table:
            duplicate_names.append(table)
        by_table[table] = path

    expected = set(REQUIRED_COLUMNS)
    actual = set(by_table)
    problems: list[str] = []
    if missing_tables := sorted(expected - actual):
        problems.append(f"fontes ausentes: {', '.join(missing_tables)}")
    if unexpected_tables := sorted(actual - expected):
        problems.append(f"fontes inesperadas: {', '.join(unexpected_tables)}")
    if duplicate_names:
        problems.append(f"nomes de tabela duplicados: {', '.join(sorted(set(duplicate_names)))}")

    for table in sorted(expected & actual):
        with by_table[table].open("r", encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), [])
        normalized = [column.strip().lower() for column in header]
        if len(normalized) != len(set(normalized)):
            problems.append(f"{table}.csv possui colunas duplicadas")
        if missing_columns := sorted(REQUIRED_COLUMNS[table] - set(normalized)):
            problems.append(f"{table}.csv sem colunas obrigatórias: {', '.join(missing_columns)}")

    if problems:
        raise SourceContractError("Contrato de fontes inválido - " + "; ".join(problems))
    return [by_table[name] for name in sorted(REQUIRED_COLUMNS)]


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
    return validate_source_contract(files)
