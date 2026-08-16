# EDA — Análise Exploratória de Dados

## Escopo

Foram examinadas **24 tabelas**, totalizando **433,424 registros**. A janela dos pedidos vai de **2020-01-01 01:19:28** a **2026-12-31 23:43:09**.

## Estrutura e integridade inicial

- Inventário completo: `tables/table_inventory.csv`.
- Ausência por coluna: `tables/missing_values.csv`.
- Estatísticas numéricas: `tables/numeric_summary.csv`.
- Distribuições de status e canal: arquivos específicos em `tables/` e `charts/`.
- Duplicidades de linha completas encontradas: **0**.

## Principais observações

- Pedidos pagos: **34,365**.
- Pedidos cancelados: **4,847**.
- O campo `stock_levels.reorder_point` está totalmente ausente e não deve ser imputado sem uma política de estoque definida.
- A ausência de vendedor em pedidos de e-commerce é compatível com o processo operacional e não é tratada como erro.
- Campos opcionais, como complemento de endereço e data de desligamento, permanecem nulos para preservar seu significado.

## Decisões decorrentes da EDA

1. Reconhecer receita somente para pedidos pagos.
2. Separar ausência estrutural de problema de qualidade.
3. Preservar dias sem venda na análise semanal.
4. Usar validação temporal na previsão para evitar vazamento de dados futuros.
5. Não automatizar reposição enquanto o ponto de reposição não estiver definido.
