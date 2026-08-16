# Modelagem de Ciência de Dados

## Previsão de demanda

A demanda mensal é a quantidade paga menos unidades reembolsadas. O modelo cobre os 50 produtos de maior giro e utiliza defasagens de 1, 2, 3, 6 e 12 meses, médias móveis, sazonalidade cíclica e tendência.

A validação preserva o tempo: os seis meses finais são teste e o restante é treino. O resultado é comparado ao baseline sazonal de 12 meses usando MAE e WAPE. O horizonte futuro é de três meses.

## Recomendações

O recomendador cria pares de produtos presentes no mesmo pedido pago. O ranking utiliza lift e publica confiança, suporte e número de cestas conjuntas.

Antes de produção, recomenda-se estabelecer suporte mínimo, filtrar estoque/atividade e executar teste A/B.

