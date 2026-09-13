select
    cast(id as bigint) as order_id,
    cast(order_number as varchar) as order_number,
    lower(trim(cast(channel as varchar))) as channel,
    cast(customer_id as bigint) as customer_id,
    cast(location_id as bigint) as location_id,
    lower(trim(cast(status as varchar))) as order_status,
    cast(subtotal as double) as subtotal,
    cast(discount_amount as double) as discount_amount,
    cast(total as double) as total,
    cast(placed_at as timestamp) as placed_at
from {{ source('raw', 'orders') }}
