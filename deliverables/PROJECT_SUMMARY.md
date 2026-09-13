# Síntese técnica e analítica

Este documento reúne os principais resultados da plataforma de dados para varejo multicanal.

## EDA

Foram avaliadas 24 tabelas e 433,424 registros. Não foram encontradas chaves primárias duplicadas nem registros órfãos nas relações verificadas. A exploração identificou ausência total do ponto de reposição e confirmou a necessidade de diferenciar nulos estruturais de falhas de qualidade. Evidências completas: `01_EDA/`.

## Tratamento de dados

Os 24 CSVs permanecem exclusivamente em `data/raw/`. Eles são tipados em memória e carregados em um DuckDB temporário. O dbt transforma e testa as camadas staging, intermediate e marts, descartadas ao final da execução. Pedidos pagos reconhecem receita; somente reembolsos concluídos são deduzidos.

## Análise geral de vendas

No período de 2020-01-01 a 2026-12-31, 34,365 pedidos pagos geraram R$ 981.065.033,66 de receita líquida e R$ 405.567.656,69 de lucro bruto estimado, com margem de 41,3%.

## Rentabilidade de produtos

Foram identificadas 94 linhas de pedido com margem negativa, somando R$ 41.093,80. O maior prejuízo transacional por produto foi **Tinta Antifouling 503**, com R$ 2.980,57. Arquivo: `03_ANALISE_DE_VENDAS/product_loss_ranking.csv`.

## Clientes com maior lucro acumulado

O cliente de maior lucro foi **Cliente 01**, com R$ 436.174,18 em 27 pedidos pagos. Os clientes foram anonimizados no material público. O ranking completo está em `04_ANALISE_DE_CLIENTES/top_customers_by_profit.csv`.

## Vendas médias por dia da semana

Todos os dias civis entre a primeira e a última venda foram materializados; dias sem venda receberam zero antes do cálculo. **Terça-feira** apresentou a maior média, R$ 395.018,92 por dia. Evidências: `03_ANALISE_DE_VENDAS/average_sales_by_weekday.csv` e `weekday_sales.png`.

## Previsão de demandas

O modelo global cobre os 50 produtos de maior giro, usa defasagens e médias móveis e foi validado nos seis meses finais. WAPE do modelo: 46,6%; baseline sazonal: 52,7%. O horizonte entregue é de três meses.

## Sistemas de recomendações

O sistema usa coocorrência em pedidos pagos e ranqueia complementos por lift. Confiança, suporte e número de pedidos conjuntos acompanham cada recomendação para permitir auditoria e definição de corte mínimo.

## Material complementar

O dashboard consolidado está em `DASHBOARD_EXECUTIVO.html`.

A relação entre cada análise e suas fontes está em `DATA_LINEAGE.md` e nos arquivos `DATA_SOURCES.md` de cada frente.
