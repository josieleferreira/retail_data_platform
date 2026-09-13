select cast(id as bigint) as customer_id, trim(cast(legal_name as varchar)) as legal_name,
       trim(cast(person_type as varchar)) as person_type
from {{ source('raw', 'customers') }}
