# Arquitetura

## Fluxo

```text
data/raw/*.csv
  -> Engenharia de Dados
     -> Limpeza e tipagem em memória
     -> EDA independente
     -> SQLite temporário em memória
     -> Marts SQL em memória
        -> Analytics
           -> KPIs, rankings, gráficos e dashboard
        -> Ciência de Dados
           -> Previsão de demanda
           -> Recomendação de produtos
  -> deliverables/ com resultados finais
```

## Persistência

Na execução local, as fontes são lidas de `data/raw/` ou de um caminho externo. Não são criados Parquets tratados, cópias intermediárias ou banco SQLite em disco. A versão pública não distribui os CSVs; `deliverables/` contém somente resultados derivados, anonimizados e a linhagem das fontes usadas.

## Engenharia de Dados

- `ingestion.py`: valida nomes e colunas obrigatórias das 24 fontes antes de importá-las para a área raw local, ignorada pelo Git.
- `transformation.py`: limpeza e tipagem em memória.
- `data_quality.py`: chaves, integridade referencial e reconciliações.
- `warehouse.py`: SQLite temporário e construção dos marts em memória.

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
