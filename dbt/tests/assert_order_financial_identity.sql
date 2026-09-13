select order_id
from {{ ref('stg_orders') }}
where abs((subtotal - discount_amount) - total) > 0.011
