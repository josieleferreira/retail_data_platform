with ordered as (
    select date, lag(date) over (order by date) as previous_date
    from {{ ref('mart_daily_sales') }}
)
select date
from ordered
where previous_date is not null
  and date_diff('day', previous_date, date) <> 1
