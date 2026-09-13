select cast(id as bigint) as return_id, cast(order_id as bigint) as order_id,
       lower(trim(cast(status as varchar))) as return_status
from {{ source('raw', 'returns') }}
