select
    ri.order_item_id,
    sum(case when ri.return_action = 'refund' then ri.quantity else 0 end) as refunded_qty,
    sum(case when ri.return_action = 'refund' then ri.quantity * ri.unit_refund_amount else 0 end) as refund_amount
from {{ ref('stg_return_items') }} ri
inner join {{ ref('stg_returns') }} r
    on r.return_id = ri.return_id
   and r.return_status = 'completed'
group by ri.order_item_id
