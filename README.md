# Retail Data Platform

![Capa do projeto Retail Data Platform](assets/portfolio-cover.png)

Projeto de portfólio que demonstra uma solução ponta a ponta de **Engenharia de Dados, Analytics e Ciência de Dados** para uma operação fictícia de varejo multicanal. A implementação integra 24 fontes relacionais em CSV, aplica validações de qualidade, constrói marts analíticos e disponibiliza análises de vendas, clientes, previsão de demanda e recomendações de produtos.

> Os nomes da organização e do processo que originou o estudo foram removidos. As fontes brutas não são distribuídas neste repositório e os resultados de clientes foram anonimizados.

## Visão geral

O projeto organiza uma base operacional fragmentada em um fluxo reproduzível:

```mermaid
flowchart LR
    A["24 fontes CSV"] --> B["Ingestão e tipagem"]
    B --> C["Validações de qualidade"]
    C --> Q["Quality gates"]
    Q --> D["DuckDB temporário"]
    D --> E["dbt: staging, intermediate e marts"]
    E --> F["EDA e Analytics"]
    E --> G["Previsão de demanda"]
    E --> H["Recomendação de produtos"]
    F --> I["Dashboard e resultados"]
    G --> I
    H --> I
    B --> J["Auditoria e fingerprints SHA-256"]
    D --> K["Linhagem JSON / OpenLineage"]
```

Não há persistência de camadas intermediárias: a transformação, o banco temporário e os marts existem somente durante a execução. Apenas resultados agregados e não identificáveis são mantidos em `deliverables/`.

## Principais resultados

- 24 tabelas e 433.424 registros avaliados.
- Nenhuma chave primária duplicada ou relação órfã nas 20 chaves estrangeiras verificadas.
- Receita líquida analisada de R$ 981,1 milhões e margem bruta estimada de 41,3% no cenário fictício.
- Calendário diário completo, incluindo dias sem vendas no cálculo das médias semanais.
- Modelo de previsão para os 50 produtos de maior giro no treino, com WAPE de 46,6% contra 52,7% do baseline sazonal.
- Recomendador item a item baseado em coocorrência, com suporte, confiança e lift para auditoria.
- Identificação de uma lacuna operacional crítica: ponto de reposição ausente em 100% dos registros de estoque.

## Componentes

### Engenharia de Dados

- Ingestão segura de pasta ou ZIP.
- Contrato explícito para nomes de fontes e colunas obrigatórias.
- Normalização de tipos e tratamento em memória.
- Auditoria de chaves, integridade referencial e identidades financeiras.
- Transformações versionadas em dbt, separadas em staging, intermediate e marts.
- Testes dbt de chaves, relacionamentos, reconciliação financeira e calendário.
- Linhagem entre fontes e análises.
- Manifesto de execução com status, duração, contagens, schemas e fingerprints SHA-256.
- Quality gates críticos que interrompem o pipeline e alertas não bloqueantes.
- Catálogo com domínio, papéis responsáveis, classificação, retenção e SLA.
- Linhagem em nível de dataset e de colunas críticas, com evento compatível com OpenLineage.

### Analytics

- KPIs comerciais, canais e evolução mensal.
- Rentabilidade e ranking de perdas por produto.
- Clientes de maior lucro acumulado, publicados com rótulos anônimos.
- Venda média por dia da semana considerando datas sem movimento.

### Ciência de Dados

- Previsão mensal com validação temporal, defasagens e médias móveis.
- Comparação objetiva com baseline sazonal por MAE e WAPE.
- Recomendação de produtos por afinidade de cestas pagas.

## Tecnologias

`Python` · `dbt` · `DuckDB` · `Pandas` · `NumPy` · `SQL` · `scikit-learn` · `Matplotlib` · `Seaborn` · `Jinja2`

## Estrutura

```text
retail_data_platform/
|-- data/raw/                  # fontes não incluídas no repositório público
|-- deliverables/              # resultados agregados, gráficos e dashboard
|-- docs/                      # arquitetura, regras, metodologia e modelagem
|-- metadata/                  # catálogo, glossário, qualidade e linhagem declarada
|-- artifacts/examples/        # evidências sanitizadas de governança
|-- dbt/                       # sources, staging, intermediate, marts e testes SQL
|-- src/retail_data_platform/
|   |-- data_engineering/
|   |-- eda/
|   |-- analytics/
|   |-- data_science/
|   `-- orchestration/
|-- tests/
|-- config.json
|-- requirements.txt
`-- run_pipeline.py
```

## Execução local

Crie o ambiente e instale as dependências:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Disponibilize as 24 fontes compatíveis em `data/raw/` ou informe uma pasta/ZIP externo:

```powershell
.venv\Scripts\python run_pipeline.py
.venv\Scripts\python run_pipeline.py --source "C:\caminho\fontes_csv"
.venv\Scripts\python run_pipeline.py --source "C:\caminho\fontes.zip"
```

## Testes

```powershell
python -m unittest discover -s tests -v
```

Os testes públicos usam dados sintéticos para validar ingestão, contrato de schema, segurança de ZIP, modelos e testes dbt, regras financeiras e seleção temporal da previsão. As reconciliações sobre o conjunto completo são ignoradas quando os 24 CSVs privados não estão presentes.

## Privacidade e publicação

- CSVs originais e dados pessoais não fazem parte da versão pública.
- Rankings de clientes utilizam rótulos como `Cliente 01`.
- O contexto empresarial foi generalizado para varejo multicanal fictício.
- O histórico da avaliação, respostas numeradas e arquivos de submissão foram removidos.

Consulte [docs/PRIVACY.md](docs/PRIVACY.md) antes de publicar novas saídas.

## Governança e auditoria

Cada execução cria artefatos locais em `artifacts/runtime/`, ignorados pelo Git:

- `audit/<run_id>/run_manifest.json`: etapas, status, métricas estruturais, hashes e resultados dos gates;
- `lineage/<run_id>.json` e `.mmd`: linhagem técnica e representação Mermaid;
- `lineage/<run_id>.openlineage.json`: evento interoperável de conclusão.
- `dbt/<run_id>/target/`: `manifest.json`, catálogo e resultados dos modelos/testes dbt.

Os manifestos registram somente nomes lógicos, nomes de arquivos, contagens, hashes e caminhos relativos. Valores brutos, mensagens de erro e caminhos absolutos não são persistidos. Consulte [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

## Limitações

- O custo utilizado é o custo cadastral atual, não o custo histórico por lote.
- Frete, impostos efetivos e despesas operacionais não estão disponíveis.
- A previsão apoia decisões, mas não substitui política de estoque, lead time e nível de serviço.
- Recomendações de baixa frequência exigem corte mínimo de suporte e validação por teste A/B.

## Materiais

- [Dashboard executivo](deliverables/DASHBOARD_EXECUTIVO.pdf)
- [Síntese técnica e analítica](deliverables/PROJECT_SUMMARY.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Metodologia e limitações](docs/METODOLOGIA.md)
- [Governança, auditoria e linhagem](docs/GOVERNANCE.md)
- [Transformações com dbt e DuckDB](docs/DBT.md)
