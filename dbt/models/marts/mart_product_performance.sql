select
    product_id,
    product_name,
    category_name,
    brand_name,
    count(distinct order_id) as orders,
    sum(quantity) as units,
    sum(gross_revenue) as gross_revenue,
    sum(net_revenue) as net_revenue,
    sum(adjusted_cogs) as adjusted_cogs,
    sum(gross_profit) as gross_profit,
    case when sum(net_revenue) = 0 then null else sum(gross_profit) / sum(net_revenue) end as margin_pct,
    sum(refunded_qty) as refunded_units,
    sum(refund_amount) as refunded_amount
from {{ ref('mart_sales_items') }}
group by product_id, product_name, category_name, brand_name
