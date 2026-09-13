# Arquitetura

## Fluxo

```text
data/raw/*.csv
  -> Engenharia de Dados
     -> Contrato de fontes + fingerprint SHA-256
     -> Limpeza e tipagem em memória
     -> Qualidade + quality gates
     -> EDA independente
     -> DuckDB temporário
     -> dbt build
        -> staging
        -> intermediate
        -> marts
        -> testes e documentação
        -> Analytics
           -> KPIs, rankings, gráficos e dashboard
        -> Ciência de Dados
           -> Previsão de demanda
           -> Recomendação de produtos
  -> deliverables/ com resultados finais
  -> artifacts/runtime/ com auditoria e linhagem local
```

## Persistência

Na execução local, as fontes são lidas de `data/raw/` ou de um caminho externo. Python aplica o contrato e carrega as tabelas tipadas em um arquivo DuckDB dentro da pasta temporária da execução. O `dbt build` cria e testa as camadas analíticas nesse banco descartável. Não são criadas cópias intermediárias permanentes; a versão pública não distribui os CSVs.

## Engenharia de Dados

- `ingestion.py`: valida nomes e colunas obrigatórias das 24 fontes antes de importá-las para a área raw local, ignorada pelo Git.
- `transformation.py`: limpeza e tipagem em memória.
- `data_quality.py`: chaves, integridade referencial e reconciliações.
- `dbt_warehouse.py`: carga no DuckDB temporário, execução do dbt e leitura dos marts.
- `dbt/models/`: fontes, staging, transformações intermediárias e marts.
- `dbt/tests/`: reconciliações financeiras, calendário e consistência entre marts.

## EDA

`eda/exploratory_analysis.py` produz inventário, valores ausentes, estatísticas numéricas e distribuições em `deliverables/01_EDA/`.

## Analytics

- `sales_analysis.py`: KPIs, canais, série mensal e dia da semana.
- `customer_analysis.py`: cliente 360 e ranking por lucro.
- `product_analysis.py`: rentabilidade e prejuízos transacionais.
- `reporting.py`: dashboard executivo.

## Ciência de Dados

- `demand_forecasting.py`: features temporais, backtest e previsão futura.
- `product_recommender.py`: afinidade item-a-item por coocorrência.

## Orquestração e linhagem

`orchestration/pipeline.py` executa o fluxo completo. Arquivos técnicos intermediários são criados em uma pasta temporária do sistema e descartados ao final.

`orchestration/presentation.py` grava somente os resultados finais nas seis frentes e gera `DATA_LINEAGE.md` e um `DATA_SOURCES.md` em cada análise.

O pacote `governance/` mantém o manifesto de execução, aplica regras de qualidade configuráveis, valida o catálogo e gera linhagem técnica em JSON, Mermaid e evento OpenLineage. Esses artefatos operacionais ficam em `artifacts/runtime/` e não são versionados; exemplos sanitizados ficam em `artifacts/examples/`.
