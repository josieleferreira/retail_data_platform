select 1
where abs(
    (select coalesce(sum(net_revenue), 0) from {{ ref('mart_sales_items') }})
    - (select coalesce(sum(net_revenue), 0) from {{ ref('mart_customer_360') }})
) > 0.011
