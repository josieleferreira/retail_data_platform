# Transformações com dbt e DuckDB

## Responsabilidades

Python continua responsável pela ingestão segura, validação do contrato de fontes, tipagem, auditoria, ciência de dados e publicação. O dbt passa a ser a camada oficial de transformação analítica:

```text
DataFrames tipados
  -> DuckDB temporário / schema raw
  -> dbt staging
  -> dbt intermediate
  -> dbt marts
  -> Analytics e Ciência de Dados
```

O banco DuckDB existe apenas na pasta temporária da execução e é descartado ao final. Não há uma segunda cópia permanente dos dados brutos.

## Estrutura

- `models/sources.yml`: declaração das 24 fontes e classificação.
- `models/staging/`: padronização dos campos necessários às análises.
- `models/intermediate/`: devoluções concluídas e composição financeira por item.
- `models/marts/`: vendas por item, cliente 360, produtos e calendário diário.
- `tests/`: identidades financeiras, calendário contínuo e reconciliação entre marts.
- `macros/generate_schema_name.sql`: schemas previsíveis no DuckDB.

## Execução integrada

```powershell
python run_pipeline.py --source "C:\caminho\fontes_csv"
```

O pipeline executa `dbt build`, que cria os modelos e aplica todos os testes, seguido de `dbt docs generate`. Os artefatos `manifest.json`, `catalog.json` e `run_results.build.json` ficam em `artifacts/runtime/dbt/<run_id>/target/` e são vinculados ao manifesto de auditoria.

## Execução isolada para desenvolvimento

O profile usa `DBT_DUCKDB_PATH` para apontar para um DuckDB que contenha as fontes no schema `raw`:

```powershell
$env:DBT_DUCKDB_PATH = "C:\caminho\retail_runtime.duckdb"
dbt build --project-dir dbt --profiles-dir dbt
dbt docs generate --project-dir dbt --profiles-dir dbt
dbt docs serve --project-dir dbt --profiles-dir dbt
```

O arquivo informado nessa execução manual não deve ser commitado.
