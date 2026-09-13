with paid_orders as (
    select * from {{ ref('stg_orders') }} where order_status = 'paid'
),
joined as (
    select
        oi.order_item_id,
        o.order_id,
        o.order_number,
        cast(o.placed_at as date) as order_date,
        o.customer_id,
        o.channel,
        o.location_id,
        oi.product_variant_id,
        pv.product_id,
        p.product_name,
        p.category_id,
        c.category_name,
        p.brand_id,
        b.brand_name,
        oi.quantity,
        oi.unit_price,
        oi.line_total as gross_revenue,
        case
            when o.subtotal = 0 then 0
            else oi.line_total * o.discount_amount / o.subtotal
        end as allocated_discount,
        coalesce(cr.refunded_qty, 0) as refunded_qty,
        coalesce(cr.refund_amount, 0) as refund_amount,
        pv.cost_price
    from {{ ref('stg_order_items') }} oi
    inner join paid_orders o on o.order_id = oi.order_id
    inner join {{ ref('stg_product_variants') }} pv on pv.product_variant_id = oi.product_variant_id
    inner join {{ ref('stg_products') }} p on p.product_id = pv.product_id
    left join {{ ref('stg_categories') }} c on c.category_id = p.category_id
    left join {{ ref('stg_brands') }} b on b.brand_id = p.brand_id
    left join {{ ref('int_completed_returns') }} cr on cr.order_item_id = oi.order_item_id
)
select
    * exclude (cost_price),
    gross_revenue - allocated_discount as revenue_after_discount,
    gross_revenue - allocated_discount - refund_amount as net_revenue,
    (quantity - refunded_qty) * cost_price as adjusted_cogs,
    gross_revenue - allocated_discount - refund_amount
        - ((quantity - refunded_qty) * cost_price) as gross_profit
from joined
