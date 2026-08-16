# Dicionário das camadas analíticas

## `mart_sales_items`

Grão: um item de pedido pago. Contém data, cliente, canal, local, SKU/produto, marca/categoria, quantidades, receita bruta, desconto alocado, reembolso, receita líquida, custo ajustado e lucro bruto.

## `mart_customer_360`

Grão: um cliente. Contém datas da primeira/última compra, pedidos pagos, unidades, receita, lucro, ticket médio e reembolso.

## `mart_product_performance`

Grão: um produto. Contém pedidos, unidades, receita, custo, lucro, margem e devoluções.

## `mart_daily_sales`

Grão: um dia civil entre a primeira e a última venda paga. Dias sem venda são materializados com zero. Esse detalhe é obrigatório para médias semanais sem viés.

## Arquivos de ciência de dados

- `forecast_backtest.csv`: realizado, previsão do modelo e baseline no período de teste.
- `demand_forecast_3_months.csv`: previsão por produto e mês.
- `product_recommendations.csv`: produto origem, recomendado, pedidos conjuntos, confiança, lift e suporte.

