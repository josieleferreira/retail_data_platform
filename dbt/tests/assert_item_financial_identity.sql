select order_item_id
from {{ ref('stg_order_items') }}
where abs((quantity * unit_price) - line_total) > 0.011
