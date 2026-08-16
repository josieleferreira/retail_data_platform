# Regras de negócio

- Reconhecer receita apenas para pedidos `paid`.
- Alocar o desconto proporcionalmente ao valor bruto de cada item.
- Deduzir somente devoluções `completed` cuja ação seja `refund`.
- Reverter o custo das unidades efetivamente reembolsadas.
- Calcular lucro bruto como receita líquida menos custo ajustado.
- Materializar dias sem venda com zero antes da média por dia da semana.
- Não considerar dados pessoais como features dos modelos.

O custo disponível é o custo atual do cadastro do SKU, não o custo histórico por lote. Portanto, lucro bruto é uma estimativa gerencial e não um resultado contábil completo.

