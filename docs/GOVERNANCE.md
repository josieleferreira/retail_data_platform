# Governança, auditoria e linhagem

## Objetivo

Os controles desta camada permitem responder, para cada execução: quais fontes foram usadas, se elas mudaram, quais regras foram aplicadas, quais produtos de dados foram gerados e qual transformação conecta cada saída aos seus dados de origem.

## Auditoria de execução

O pipeline cria um `run_id` único e grava `artifacts/runtime/audit/<run_id>/run_manifest.json`. O manifesto contém:

- início, término, duração e status da execução e de cada etapa;
- nome lógico, contagem de linhas, quantidade de colunas e hash do schema;
- nome, tamanho e fingerprint SHA-256 de cada fonte;
- resultados observados e limites de cada quality gate;
- caminhos relativos, tamanhos e hashes dos artefatos publicados;
- tipo da exceção em caso de falha, sem armazenar mensagem ou valores dos dados.

Os caminhos absolutos e os valores das linhas não entram no manifesto. O diretório operacional é ignorado pelo Git.

## Quality gates

As regras estão em `metadata/quality_rules.json` e possuem identificador, métrica, operador, limite e severidade:

- `ERROR`: interrompe o pipeline antes da construção dos marts;
- `WARNING`: registra a não conformidade sem bloquear a entrega.

Duplicidade de chave primária, registros órfãos e falhas nas reconciliações financeiras são bloqueantes. A ausência de ponto de reposição é mantida como alerta porque representa uma lacuna operacional conhecida, e não corrupção dos dados de vendas.

## Catálogo e responsabilidades

`metadata/datasets.json` descreve fontes, marts e saídas públicas. Cada entrada informa camada, domínio, papel proprietário, papel steward, classificação, presença de PII, retenção e SLA.

Os nomes de pessoas não são usados como responsáveis. A atribuição por papel facilita a continuidade operacional e evita expor dados pessoais no repositório.

## Classificação e acesso

- `PUBLIC`: resultado agregado aprovado para portfólio;
- `INTERNAL`: dado operacional sem autorização para publicação;
- `CONFIDENTIAL`: dado comercial ou financeiro restrito;
- `RESTRICTED_PII`: dado pessoal sujeito a finalidade, retenção e acesso mínimo.

Uma validação automatizada impede que um dataset classificado como público seja marcado como contendo PII. A anonimização das saídas continua sendo uma etapa obrigatória antes da publicação.

## Linhagem

`metadata/lineage.json` declara dependências em nível de dataset e a derivação das colunas financeiras críticas. Ao final da execução são gerados:

- JSON de linhagem com `run_id`;
- diagrama Mermaid;
- evento de conclusão compatível com a estrutura do OpenLineage.
- `manifest.json` do dbt com o DAG efetivamente compilado entre sources, staging, intermediate, marts e testes.
- `catalog.json` do dbt com relações e colunas observadas no DuckDB temporário.
- `run_results.build.json` com o status e tempo de cada modelo e teste.

A validação falha caso uma saída obrigatória não possua ao menos um upstream declarado.

## Evidências e operação

Para auditar uma execução:

1. confirme que o manifesto terminou com `COMPLETED`;
2. verifique que todos os gates `ERROR` possuem `passed: true`;
3. compare os SHA-256 das fontes com a execução anterior;
4. confirme a linhagem das saídas afetadas;
5. revise o `run_results.build.json` e confirme que nenhum nó dbt falhou;
6. valide hashes e caminhos relativos dos artefatos publicados;
7. registre e aprove exceções antes de promover a entrega.

Os testes em `tests/governance/` cobrem fechamento de execuções com sucesso e falha, privacidade do manifesto, bloqueio de quality gates, completude do catálogo e cobertura da linhagem.
