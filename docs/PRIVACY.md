# Privacidade e anonimização

## Escopo público

Esta edição foi preparada para portfólio. Foram removidos o nome da organização, referências ao processo de avaliação, arquivos de submissão e as fontes CSV originais.

## Dados de clientes

Os marts internos podem usar identificadores para realizar relacionamentos, mas os resultados publicados não apresentam nome, documento, e-mail, telefone ou endereço. Rankings usam rótulos sequenciais (`Cliente 01`, `Cliente 02` etc.), definidos apenas pela posição agregada.

## Antes de atualizar o repositório

1. Não versionar arquivos em `data/raw/`.
2. Não publicar bancos temporários, arquivos de ambiente ou logs de execução.
3. Revisar novas tabelas e gráficos em busca de nomes e identificadores.
4. Executar a busca descrita abaixo antes do commit.

```powershell
rg -n -i "legal_name|trade_name|tax_id|email|phone|address" deliverables
```

Menções a nomes de colunas em documentação técnica podem ser legítimas; valores reais dessas colunas não devem aparecer.

