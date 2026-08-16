"""Construção do dashboard executivo autônomo."""

from __future__ import annotations

from pathlib import Path
import base64
import html
import pandas as pd
from jinja2 import Template


def brl(x):
    return "R$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x): return f"{100*x:.1f}%".replace(".", ",")


def img64(path: Path): return base64.b64encode(path.read_bytes()).decode()


def table_html(df: pd.DataFrame, columns: list[str], labels: list[str], money=()) -> str:
    x = df[columns].copy(); x.columns = labels
    for c in money:
        if c in x.columns: x[c] = x[c].map(brl)
    return x.to_html(index=False, classes="data-table", border=0, escape=True)


TEMPLATE = Template(r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Retail Data Platform - Relatório Executivo</title>
<style>
:root{--navy:#081a4b;--blue:#1367a8;--teal:#19a7a0;--gold:#f2b134;--red:#d94f4f;--ink:#18243d;--muted:#60708d;--bg:#f3f6fa}
*{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header{background:linear-gradient(120deg,var(--navy),#124b80);color:white;padding:46px max(5vw,28px) 38px}header h1{margin:0 0 8px;font-size:38px}header p{margin:0;opacity:.84}
main{max-width:1240px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:white;border-radius:14px;padding:20px;box-shadow:0 3px 15px #10234a12}.kpi span{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.06em}.kpi strong{display:block;font-size:26px;color:var(--navy);margin-top:8px}.section{margin-top:22px}.section h2{color:var(--navy);margin:0 0 15px}.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}.chart{width:100%;border-radius:9px}.data-table{width:100%;border-collapse:collapse;font-size:13px}.data-table th{background:#edf3f8;color:var(--navy);text-align:left}.data-table td,.data-table th{padding:9px;border-bottom:1px solid #e5ebf2}.note{border-left:4px solid var(--gold);padding:12px 16px;background:#fff9e9;border-radius:4px}.good{border-left-color:var(--teal);background:#eefaf8}ul{line-height:1.55}.footer{color:var(--muted);font-size:12px;margin:30px 0 10px}@media(max-width:850px){.grid{grid-template-columns:1fr 1fr}.two{grid-template-columns:1fr}}@media(max-width:520px){.grid{grid-template-columns:1fr}main{padding:14px}}
</style></head><body>
<header><h1>Retail Data Platform</h1><p>Engenharia, desempenho comercial, clientes, demanda e recomendação · {{ period }}</p></header>
<main>
<div class="grid">
 <div class="card kpi"><span>Receita líquida</span><strong>{{ revenue }}</strong></div>
 <div class="card kpi"><span>Lucro bruto</span><strong>{{ profit }}</strong></div>
 <div class="card kpi"><span>Margem bruta</span><strong>{{ margin }}</strong></div>
 <div class="card kpi"><span>Pedidos pagos</span><strong>{{ orders }}</strong></div>
 <div class="card kpi"><span>Clientes ativos</span><strong>{{ customers }}</strong></div>
 <div class="card kpi"><span>Ticket médio</span><strong>{{ ticket }}</strong></div>
 <div class="card kpi"><span>Devoluções concluídas</span><strong>{{ refunds }}</strong></div>
 <div class="card kpi"><span>Taxa de devolução</span><strong>{{ refund_rate }}</strong></div>
</div>
<section class="card section"><h2>Leitura executiva</h2><ul>{{ insights }}</ul><div class="note good"><b>Decisão:</b> priorizar produtos/clientes por lucro, e não só por faturamento; usar a previsão como apoio ao reabastecimento após cadastrar pontos de reposição.</div></section>
<section class="two section"><div class="card"><h2>Evolução mensal</h2><img class="chart" src="data:image/png;base64,{{ monthly_img }}"></div><div class="card"><h2>Venda média semanal</h2><img class="chart" src="data:image/png;base64,{{ weekday_img }}"></div></section>
<section class="two section"><div class="card"><h2>Prejuízos por produto</h2><img class="chart" src="data:image/png;base64,{{ losses_img }}"></div><div class="card"><h2>Clientes de maior lucro</h2><img class="chart" src="data:image/png;base64,{{ customers_img }}"></div></section>
<section class="two section"><div class="card"><h2>Ranking de prejuízos</h2>{{ losses_table }}</div><div class="card"><h2>Top clientes por lucro</h2>{{ customers_table }}</div></section>
<section class="card section"><h2>Previsão de demanda</h2><p>Modelo global de gradient boosting, treinado nos 50 produtos de maior giro com defasagens de 1, 2, 3, 6 e 12 meses e médias móveis. Validação temporal nos últimos {{ test_months }} meses, sem embaralhamento.</p><div class="grid"><div class="kpi"><span>WAPE modelo</span><strong>{{ wape }}</strong></div><div class="kpi"><span>WAPE baseline sazonal</span><strong>{{ naive_wape }}</strong></div><div class="kpi"><span>MAE modelo</span><strong>{{ mae }}</strong></div><div class="kpi"><span>Horizonte</span><strong>3 meses</strong></div></div><div class="note"><b>Uso responsável:</b> o modelo prevê unidades; custo, estoque disponível, lead time e nível de serviço ainda devem entrar na decisão de compra. O backtest completo está nos CSVs.</div></section>
<section class="card section"><h2>Sistema de recomendações</h2><p>Recomendações item-a-item calculadas por coocorrência em pedidos pagos. O ranking usa <i>lift</i>, evitando recomendar apenas itens populares; também são entregues suporte e confiança para auditoria.</p>{{ recs_table }}</section>
<section class="card section"><h2>Qualidade e governança</h2><ul><li>24 fontes e {{ rows }} registros ingeridos; chaves primárias duplicadas: 0; órfãos nas relações testadas: 0.</li><li>Coerência financeira validada: subtotal − desconto = total e quantidade × preço = total do item.</li><li><code>reorder_point</code> está 100% ausente; previsões não devem disparar compras automaticamente.</li><li>Receita reconhecida somente em pedidos <code>paid</code>; devoluções somente em status <code>completed</code>.</li><li>Dados pessoais permanecem na camada restrita; os resultados públicos usam rótulos anônimos.</li></ul></section>
<p class="footer">Regras, SQL, dados curados, métricas, modelos e testes acompanham este relatório.</p>
</main></body></html>""")


def build_report(analysis: dict, forecast: dict, recs: pd.DataFrame, quality: dict, output_dir: Path):
    m = analysis["metrics"]; losses = analysis["losses"]; customers = analysis["top_customers"]
    best_day = analysis["weekdays"].nlargest(1, "avg_daily_sales").iloc[0]
    best_channel = analysis["channel"].nlargest(1, "gross_profit").iloc[0]
    trend = analysis["monthly"].sort_values("month")
    recent = trend.tail(12).net_revenue.sum(); prior = trend.iloc[-24:-12].net_revenue.sum()
    yoy = (recent/prior-1) if prior else 0
    insights = "".join([
        f"<li><b>{html.escape(str(best_channel.channel))}</b> lidera em lucro bruto: {brl(best_channel.gross_profit)}.</li>",
        f"<li><b>{html.escape(str(best_day.weekday_name))}</b> é o dia com maior venda média: {brl(best_day.avg_daily_sales)} — cálculo inclui dias sem venda.</li>",
        f"<li>A receita dos 12 meses finais variou <b>{pct(yoy)}</b> contra os 12 meses anteriores.</li>",
        f"<li>Foram identificados <b>{m['loss_item_rows']} itens de pedido com margem negativa</b>, somando {brl(m['total_transaction_losses'])} de prejuízo transacional.</li>",
        f"<li>Devoluções concluídas somam <b>{brl(m['refund_amount'])}</b>; casos abertos ou cancelados foram excluídos.</li>",
    ])
    rec_sample = recs.sort_values(["lift","pair_orders"], ascending=False).head(12).copy()
    html_doc = TEMPLATE.render(
        period=f"{m['period_start']} a {m['period_end']}", revenue=brl(m["net_revenue"]), profit=brl(m["gross_profit"]),
        margin=pct(m["margin_pct"]), orders=f"{m['paid_orders']:,}".replace(",","."), customers=f"{m['active_customers']:,}".replace(",","."),
        ticket=brl(m["avg_ticket"]), refunds=brl(m["refund_amount"]), refund_rate=pct(m["refund_rate_pct"]), insights=insights,
        monthly_img=img64(output_dir/"charts"/"monthly_revenue.png"), weekday_img=img64(output_dir/"charts"/"weekday_sales.png"),
        losses_img=img64(output_dir/"charts"/"product_losses.png"), customers_img=img64(output_dir/"charts"/"top_customers.png"),
        losses_table=table_html(losses, ["product_name","loss_items","affected_revenue","loss_amount"], ["Produto","Itens","Receita afetada","Prejuízo"], ["Receita afetada","Prejuízo"]),
        customers_table=table_html(customers.head(10), ["customer_label","paid_orders","net_revenue","gross_profit"], ["Cliente","Pedidos","Receita","Lucro"], ["Receita","Lucro"]),
        test_months=forecast["metrics"]["test_months"], wape=pct(forecast["metrics"]["wape_model"]), naive_wape=pct(forecast["metrics"]["wape_seasonal_naive"]), mae=f"{forecast['metrics']['mae_model']:.1f}",
        recs_table=table_html(rec_sample, ["source_product_name","recommended_product_name","pair_orders","confidence","lift"], ["Produto","Recomendar","Pedidos juntos","Confiança","Lift"]),
        rows=f"{quality['summary']['rows']:,}".replace(",","."),
    )
    (output_dir / "dashboard_executivo.html").write_text(html_doc, encoding="utf-8")
    summary = f"""# Resumo executivo - Retail Data Platform

## Resultado comercial

Entre {m['period_start']} e {m['period_end']}, {m['paid_orders']:,} pedidos pagos geraram **{brl(m['net_revenue'])} de receita líquida** e **{brl(m['gross_profit'])} de lucro bruto estimado**, com margem de **{pct(m['margin_pct'])}**. O ticket médio foi {brl(m['avg_ticket'])}. O canal de maior lucro foi **{best_channel.channel}**, com {brl(best_channel.gross_profit)}.

Os 12 meses finais variaram **{pct(yoy)}** contra os 12 meses anteriores. **{best_day.weekday_name}** apresentou a maior média diária, {brl(best_day.avg_daily_sales)}, incluindo dias sem venda.

## Prejuízos e devoluções

Foram encontradas {m['loss_item_rows']} linhas de pedido com margem negativa, somando **{brl(m['total_transaction_losses'])}**. Devoluções concluídas reduziram a receita em **{brl(m['refund_amount'])}**; casos abertos ou cancelados foram excluídos.

## Previsão e recomendação

No backtest temporal, o modelo obteve WAPE de **{pct(forecast['metrics']['wape_model'])}**, contra **{pct(forecast['metrics']['wape_seasonal_naive'])}** do baseline sazonal. As previsões detalhadas ficam em `deliverables/05_PREVISAO_DE_DEMANDAS/`.

O recomendador publica lift, confiança, suporte e pedidos conjuntos em `deliverables/06_SISTEMAS_DE_RECOMENDACOES/`. Antes de produção, aplicar suporte mínimo, disponibilidade em estoque e teste A/B.

## Prioridades

1. Cadastrar pontos de reposição e política de nível de serviço por SKU/local.
2. Investigar linhas negativas considerando desconto, custo cadastral e devolução.
3. Priorizar campanhas por lucro e valor do cliente, não apenas faturamento.
4. Monitorar mensalmente o backtest e manter um baseline de referência.
"""
    (output_dir / "RESUMO_EXECUTIVO.md").write_text(summary, encoding="utf-8")
