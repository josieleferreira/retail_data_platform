DROP VIEW IF EXISTS mart_sales_items;
CREATE VIEW mart_sales_items AS
WITH completed_returns AS (
    SELECT ri.order_item_id,
           SUM(CASE WHEN ri.action = 'refund' THEN ri.quantity ELSE 0 END) AS refunded_qty,
           SUM(CASE WHEN ri.action = 'refund' THEN ri.quantity * ri.unit_refund_amount ELSE 0 END) AS refund_amount
    FROM return_items ri
    JOIN returns r ON r.id = ri.return_id AND r.status = 'completed'
    GROUP BY ri.order_item_id
)
SELECT
    oi.id AS order_item_id, o.id AS order_id, o.order_number, DATE(o.placed_at) AS order_date,
    o.customer_id, o.channel, o.location_id, oi.product_variant_id, pv.product_id,
    p.name AS product_name, p.category_id, c.name AS category_name, p.brand_id, b.name AS brand_name,
    oi.quantity, oi.unit_price, oi.line_total AS gross_revenue,
    CASE WHEN o.subtotal = 0 THEN 0 ELSE oi.line_total * o.discount_amount / o.subtotal END AS allocated_discount,
    oi.line_total - CASE WHEN o.subtotal = 0 THEN 0 ELSE oi.line_total * o.discount_amount / o.subtotal END AS revenue_after_discount,
    COALESCE(cr.refunded_qty, 0) AS refunded_qty, COALESCE(cr.refund_amount, 0) AS refund_amount,
    (oi.line_total - CASE WHEN o.subtotal = 0 THEN 0 ELSE oi.line_total * o.discount_amount / o.subtotal END) - COALESCE(cr.refund_amount, 0) AS net_revenue,
    (oi.quantity - COALESCE(cr.refunded_qty, 0)) * pv.cost_price AS adjusted_cogs,
    ((oi.line_total - CASE WHEN o.subtotal = 0 THEN 0 ELSE oi.line_total * o.discount_amount / o.subtotal END) - COALESCE(cr.refund_amount, 0))
       - (oi.quantity - COALESCE(cr.refunded_qty, 0)) * pv.cost_price AS gross_profit
FROM order_items oi
JOIN orders o ON o.id = oi.order_id AND o.status = 'paid'
JOIN product_variants pv ON pv.id = oi.product_variant_id
JOIN products p ON p.id = pv.product_id
LEFT JOIN categories c ON c.id = p.category_id
LEFT JOIN brands b ON b.id = p.brand_id
LEFT JOIN completed_returns cr ON cr.order_item_id = oi.id;

