select cast(id as bigint) as brand_id, trim(cast(name as varchar)) as brand_name
from {{ source('raw', 'brands') }}
