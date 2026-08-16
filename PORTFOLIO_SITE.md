# Texto para o Google Sites

## Título

Plataforma de Dados para Varejo Multicanal

## Descrição

O projeto Retail Data Platform teve como objetivo transformar 24 fontes operacionais em uma solução integrada de Engenharia de Dados, Analytics e Ciência de Dados. A arquitetura contempla ingestão de arquivos CSV, padronização de tipos, validações de qualidade e construção de marts SQL em memória, preservando a rastreabilidade das fontes sem manter cópias intermediárias.

Na etapa analítica, foram desenvolvidos indicadores de vendas, rentabilidade de produtos, desempenho por canal e valor de clientes. Também foi criada uma dimensão calendário para incluir dias sem movimentação nas médias semanais, evitando distorções e tornando os indicadores mais confiáveis para a tomada de decisão.

Na frente de Ciência de Dados, foi construído um modelo de previsão mensal para os produtos de maior giro, validado temporalmente e comparado com um baseline sazonal. O projeto também inclui um sistema de recomendação item a item baseado em coocorrência de compras, com métricas de suporte, confiança e lift.

Por fim, os resultados foram consolidados em um dashboard executivo e acompanhados por documentação de arquitetura, regras de negócio, linhagem, testes e limitações. A versão pública foi anonimizada e não contém os arquivos brutos nem dados pessoais de clientes.

Acesse o projeto: [GitHub](https://github.com/josieleferreira/retail-data-platform)

## Tecnologias

Python, SQL, Pandas, NumPy, SQLite, scikit-learn, Matplotlib, Seaborn e Jinja2.

