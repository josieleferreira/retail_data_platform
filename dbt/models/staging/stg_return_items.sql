select cast(id as bigint) as return_item_id, cast(return_id as bigint) as return_id,
       cast(order_item_id as bigint) as order_item_id, cast(quantity as double) as quantity,
       lower(trim(cast(action as varchar))) as return_action,
       cast(unit_refund_amount as double) as unit_refund_amount
from {{ source('raw', 'return_items') }}
