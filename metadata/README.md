# Metadados de governança

- `datasets.json`: catálogo, responsabilidade, classificação, retenção e SLA.
- `classifications.json`: níveis de segurança permitidos.
- `quality_rules.json`: quality gates bloqueantes e alertas.
- `lineage.json`: dependências entre fontes, marts e saídas públicas.
- `business_glossary.json`: definições de métricas e conceitos do negócio.

Os arquivos são declarativos e versionados para que mudanças nas regras sejam revisáveis por pull request.
