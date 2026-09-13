with bounds as (
    select min(order_date) as min_date, max(order_date) as max_date
    from {{ ref('mart_sales_items') }}
),
calendar as (
    select cast(calendar_date as date) as calendar_date
    from bounds,
    generate_series(min_date, max_date, interval 1 day) as dates(calendar_date)
),
daily as (
    select
        order_date,
        count(distinct order_id) as orders,
        sum(net_revenue) as net_revenue,
        sum(gross_profit) as gross_profit
    from {{ ref('mart_sales_items') }}
    group by order_date
)
select
    c.calendar_date as date,
    cast(extract(dow from c.calendar_date) as integer) as weekday,
    coalesce(d.orders, 0) as orders,
    coalesce(d.net_revenue, 0) as net_revenue,
    coalesce(d.gross_profit, 0) as gross_profit
from calendar c
left join daily d on d.order_date = c.calendar_date
