DROP VIEW IF EXISTS mart_product_performance;
CREATE VIEW mart_product_performance AS
SELECT product_id, product_name, category_name, brand_name,
       COUNT(DISTINCT order_id) AS orders, SUM(quantity) AS units,
       SUM(gross_revenue) AS gross_revenue, SUM(net_revenue) AS net_revenue,
       SUM(adjusted_cogs) AS adjusted_cogs, SUM(gross_profit) AS gross_profit,
       CASE WHEN SUM(net_revenue)=0 THEN NULL ELSE SUM(gross_profit)/SUM(net_revenue) END AS margin_pct,
       SUM(refunded_qty) AS refunded_units, SUM(refund_amount) AS refunded_amount
FROM mart_sales_items GROUP BY product_id, product_name, category_name, brand_name;

