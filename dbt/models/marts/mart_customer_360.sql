select
    c.customer_id,
    c.legal_name,
    c.person_type,
    min(s.order_date) as first_purchase_date,
    max(s.order_date) as last_purchase_date,
    count(distinct s.order_id) as paid_orders,
    sum(s.quantity) as units,
    sum(s.net_revenue) as net_revenue,
    sum(s.gross_profit) as gross_profit,
    case
        when count(distinct s.order_id) = 0 then 0
        else sum(s.net_revenue) / count(distinct s.order_id)
    end as avg_ticket,
    sum(s.refund_amount) as refunded_amount
from {{ ref('stg_customers') }} c
left join {{ ref('mart_sales_items') }} s on s.customer_id = c.customer_id
group by c.customer_id, c.legal_name, c.person_type
