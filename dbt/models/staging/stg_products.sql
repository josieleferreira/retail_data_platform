select
    cast(id as bigint) as product_id,
    trim(cast(name as varchar)) as product_name,
    cast(brand_id as bigint) as brand_id,
    cast(category_id as bigint) as category_id
from {{ source('raw', 'products') }}
