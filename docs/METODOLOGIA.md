# Metodologia, premissas e limitações

## Arquitetura

1. **Raw:** os 24 CSVs são lidos de uma área local não versionada ou de um caminho externo.
2. **Transformação:** nomes, espaços, datas, booleanos, inteiros e decimais são tratados em memória.
3. **SQL temporário:** as fontes são carregadas em SQLite `:memory:` e os índices existem somente durante a execução.
4. **Marts em memória:** vendas por item, cliente 360, desempenho de produto e calendário diário completo.
5. **Data Science:** previsão global de demanda e recomendação item-a-item.
6. **Consumo:** somente resultados analíticos anonimizados e o dashboard permanecem em `deliverables/`.

## Qualidade

São verificados volume, duplicidade das chaves primárias, 20 relações de chave estrangeira, coerência de totais de pedidos e itens, janela temporal e ausência de ponto de reposição. Campos opcionais não são imputados artificialmente.

## Métricas comerciais

Pedidos `draft`, `cancelled` e `confirmed` não são receita realizada. Para pedidos pagos, o desconto é distribuído conforme a participação do item no subtotal. Somente devoluções concluídas do tipo reembolso reduzem a receita. Unidades reembolsadas revertem o custo; trocas não reduzem receita porque têm reembolso zero no conjunto fornecido.

O custo vem de `product_variants.cost_price`, que representa o cadastro atual, não um custo histórico por lote. Consequentemente, “lucro bruto” é uma estimativa gerencial, não resultado contábil ou margem fiscal. Frete, impostos efetivos e despesas operacionais não estão disponíveis.

O ranking de prejuízos soma apenas linhas de venda cujo lucro calculado ficou negativo. Separadamente, `lowest_accumulated_profit.csv` mostra os produtos de menor lucro acumulado, mesmo quando permanecem positivos no período completo.

## Clientes

O mart 360 agrega primeira e última compra, pedidos, unidades, receita, lucro, ticket e reembolsos. A publicação usa lucro acumulado e substitui a identificação por rótulos sequenciais. Dados pessoais completos permanecem apenas nas fontes locais; os resultados públicos não incluem nome, documento, telefone, e-mail ou endereço.

## Previsão de demanda

A demanda mensal é a quantidade paga menos unidades reembolsadas. Para reduzir esparsidade, o modelo cobre os 50 produtos de maior giro. Features: defasagens 1/2/3/6/12, médias móveis 3/6, mês cíclico e tendência. O teste usa os 6 meses finais, preservando a ordem temporal, e compara com baseline sazonal de 12 meses. WAPE e MAE são publicados mesmo quando o modelo perde do baseline.

A previsão não substitui política de estoque. `stock_levels.reorder_point` está vazio em 100% das linhas; antes de automatizar compras, definir nível de serviço, lead time, estoque de segurança, lote mínimo e custo de ruptura.

## Recomendação

Produtos presentes no mesmo pedido pago formam pares. Para cada produto, o sistema retorna até cinco complementos com maior lift, acompanhado de confiança, suporte e número de pedidos conjuntos. O método é explicável, mas itens frios podem não receber recomendações; em produção, aplicar suporte mínimo e teste A/B.

## Riscos temporais

A base cobre 2020–2026 e contém registros posteriores à data de criação de alguns cadastros. A execução usa a maior data de pedido disponível como corte analítico. Em produção, o corte deve ser parametrizado para garantir que nenhum dado futuro entre no treino.
