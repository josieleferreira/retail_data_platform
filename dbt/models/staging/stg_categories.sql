select cast(id as bigint) as category_id, trim(cast(name as varchar)) as category_name
from {{ source('raw', 'categories') }}
