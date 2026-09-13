select
    cast(id as bigint) as product_variant_id,
    cast(product_id as bigint) as product_id,
    cast(cost_price as double) as cost_price
from {{ source('raw', 'product_variants') }}
