DROP VIEW IF EXISTS mart_daily_sales;
CREATE VIEW mart_daily_sales AS
WITH RECURSIVE bounds AS (
  SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM mart_sales_items
), calendar(day) AS (
  SELECT min_date FROM bounds
  UNION ALL SELECT DATE(day, '+1 day') FROM calendar, bounds WHERE day < max_date
), daily AS (
  SELECT order_date, COUNT(DISTINCT order_id) AS orders, SUM(net_revenue) AS net_revenue,
         SUM(gross_profit) AS gross_profit FROM mart_sales_items GROUP BY order_date
)
SELECT c.day AS date, CAST(STRFTIME('%w', c.day) AS INTEGER) AS weekday,
       COALESCE(d.orders, 0) AS orders, COALESCE(d.net_revenue, 0) AS net_revenue,
       COALESCE(d.gross_profit, 0) AS gross_profit
FROM calendar c LEFT JOIN daily d ON d.order_date = c.day;

