select
    dispatching_base_num,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,
    sr_flag,
    affiliated_base_number
from {{ source('raw', 'fhv_tripdata') }}
-- El examen requiere filtrar los nulos, pero en Parquet/DuckDB 
-- los nulos a veces se representan como strings vacíos.
where dispatching_base_num is not null 
  and dispatching_base_num != ''