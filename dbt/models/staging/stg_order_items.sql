select
    cast(id as bigint) as order_item_id,
    cast(order_id as bigint) as order_id,
    cast(product_variant_id as bigint) as product_variant_id,
    cast(quantity as double) as quantity,
    cast(unit_price as double) as unit_price,
    cast(line_total as double) as line_total
from {{ source('raw', 'order_items') }}
