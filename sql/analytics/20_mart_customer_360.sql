DROP VIEW IF EXISTS mart_customer_360;
CREATE VIEW mart_customer_360 AS
SELECT c.id AS customer_id, c.legal_name, c.person_type,
       MIN(s.order_date) AS first_purchase_date, MAX(s.order_date) AS last_purchase_date,
       COUNT(DISTINCT s.order_id) AS paid_orders, SUM(s.quantity) AS units,
       SUM(s.net_revenue) AS net_revenue, SUM(s.gross_profit) AS gross_profit,
       CASE WHEN COUNT(DISTINCT s.order_id)=0 THEN 0 ELSE SUM(s.net_revenue)/COUNT(DISTINCT s.order_id) END AS avg_ticket,
       SUM(s.refund_amount) AS refunded_amount
FROM customers c LEFT JOIN mart_sales_items s ON s.customer_id = c.id
GROUP BY c.id, c.legal_name, c.person_type;

