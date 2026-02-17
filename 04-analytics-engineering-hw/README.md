# Module 4 Homework: Analytics Engineering with dbt

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#module-4-homework-analytics-engineering-with-dbt)

In this homework, we'll use the dbt project in `04-analytics-engineering/taxi_rides_ny/` to transform NYC taxi data and answer questions by querying the models.

## Setup

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#setup)

1. Set up your dbt project following the [setup guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/setup)
2. Load the Green and Yellow taxi data for 2019-2020 into your warehouse
3. Run `dbt build --target prod` to create all models and run tests

> **Note:** By default, dbt uses the `dev` target. You must use `--target prod` to build the models in the production dataset, which is required for the homework queries below.

After a successful build, you should have models like `fct_trips`, `dim_zones`, and `fct_monthly_zone_revenue` in your warehouse.

---

### Question 1. dbt Lineage and Execution

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-1-dbt-lineage-and-execution)

Given a dbt project with the following structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `dbt run --select int_trips_unioned`, what models will be built?

- `stg_green_tripdata`, `stg_yellow_tripdata`, and `int_trips_unioned` (upstream dependencies)
- Any model with upstream and downstream dependencies to `int_trips_unioned`
- `int_trips_unioned` only ✅
- `int_trips_unioned`, `int_trips`, and `fct_trips` (downstream dependencies)

#### Justification:
In dbt, the `--select` flag is **exclusive**. Without any graph operators (like the `+` prefix or suffix), dbt will only execute the specific model named in the command.

- **Upstream models** (`stg_green_tripdata`, `stg_yellow_tripdata`) are not built unless the `+` prefix is used (`--select +int_trips_unioned`).
    
- **Downstream models** are not built unless the `+` suffix is used (`--select int_trips_unioned+`).
    

Therefore, the command `dbt run --select int_trips_unioned` triggers the execution of **only that individual model**, assuming its dependencies already exist as tables or views in the database.

---

### Question 2. dbt Tests

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-2-dbt-tests)

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data.

What happens when you run `dbt test --select fct_trips`?

- dbt will skip the test because the model didn't change
- dbt will fail the test, returning a non-zero exit code ✅
- dbt will pass the test with a warning about the new value
- dbt will update the configuration to include the new value

#### Justification:
The `accepted_values` test is a validation rule that ensures all records in a specific column match a predefined list. When a value outside that list (in this case, `6`) appears in the data:

1. The test query identifies these "invalid" records.
    
2. Since the test finds records that violate the criteria, it triggers a **Failure** status.
    
3. dbt signals this failure to the orchestrator or terminal by returning a **non-zero exit code**, which is the standard way to indicate that the operation was unsuccessful and requires attention.

---

### Question 3. Counting Records in `fct_monthly_zone_revenue`

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-3-counting-records-in-fct_monthly_zone_revenue)

After running your dbt project, query the `fct_monthly_zone_revenue` model.

What is the count of records in the `fct_monthly_zone_revenue` model?

- 12,998
- 14,120
- 12,184 ✅
- 15,421

#### Justification:
```sql
SELECT count(*) FROM prod.fct_monthly_zone_revenue;
```

The `fct_monthly_zone_revenue` model is an aggregate table that groups granular trip data into monthly buckets per pickup zone and service type.

1. **Full Dataset Processing:** By running `dbt build` with the `--target prod` flag and `--full-refresh`, the project bypassed the development row limits and processed the entire 2019-2020 dataset (approximately 109 million records).
    
2. **Granularity:** The result of **12,184** represents the total number of unique combinations of month, pickup location, and taxi color (Yellow/Green) that recorded at least one trip during the two-year period.
    
3. **Validation:** This specific count matches the expected output for the provided dataset, confirming that the transformation logic successfully joined the fact data with the zone dimensions without losing records during the union or join phases.

---

### Question 4. Best Performing Zone for Green Taxis (2020)

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-4-best-performing-zone-for-green-taxis-2020)

Using the `fct_monthly_zone_revenue` table, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

Which zone had the highest revenue?

- East Harlem North ✅
- Morningside Heights
- East Harlem South
- Washington Heights South

#### Justification:

```sql
SELECT pickup_zone, SUM(revenue_monthly_total_amount) as total_revenue FROM prod.fct_monthly_zone_revenue WHERE service_type = 'Green' AND revenue_month >= '2020-01-01' AND revenue_month <= '2020-12-31' GROUP BY 1 ORDER BY 2 DESC LIMIT 5;
```

Using the materialized `fct_monthly_zone_revenue` table in the production schema, I performed a seasonal analysis by filtering for the 'Green' service type and the entire 2020 fiscal year. By aggregating the `revenue_monthly_total_amount` and grouping by `pickup_zone`, the data reveals which geographic area generated the highest total revenue. This top-down approach leverages the pre-calculated monthly totals, ensuring an efficient and accurate performance comparison across all NYC taxi zones.

---

### Question 5. Green Taxi Trip Counts (October 2019)

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-5-green-taxi-trip-counts-october-2019)

Using the `fct_monthly_zone_revenue` table, what is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

- 500,234
- 350,891
- 384,624 ✅
- 421,509

#### Justification:
```sql
SELECT 
    SUM(total_monthly_trips) as total_trips
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND revenue_month = '2019-10-01';
```

By querying the `fct_monthly_zone_revenue` table, I aggregated the `total_monthly_trips` metric for the 'Green' service type, specifically filtering for the month of October 2019. This demonstrates the efficiency of using pre-aggregated fact tables: instead of scanning millions of raw records from 2019, we perform a simple sum over a few dozen rows that represent the zones for that specific month, yielding a high-performance result.

---

### Question 6. Build a Staging Model for FHV Data

[](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md#question-6-build-a-staging-model-for-fhv-data)

Create a staging model for the **For-Hire Vehicle (FHV)** trip data for 2019.

1. Load the [FHV trip data for 2019](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv) into your data warehouse
2. Create a staging model `stg_fhv_tripdata` with these requirements:
    - Filter out records where `dispatching_base_num IS NULL`
    - Rename fields to match your project's naming conventions (e.g., `PUlocationID` → `pickup_location_id`)

What is the count of records in `stg_fhv_tripdata`?

- 42,084,899
- 43,244,693 ✅
- 22,998,722
- 44,112,187

#### Justification:
```bash
mkdir -p data
cd data
for month in {01..12}; do
  wget https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2019-${month}.parquet
done
cd ..
```

```sql
CREATE OR REPLACE TABLE raw_fhv_tripdata AS 
SELECT * FROM 'data/fhv_tripdata_2019-*.parquet';

-- Verifica cuántos hay en total (deberían ser unos 43 millones)
SELECT count(*) FROM raw_fhv_tripdata;
.exit
```

Register the new source in models/staging/sources.yml:
```yaml
- name: fhv_tripdata
        description: Raw for-hire vehicle (FHV) trip records for 2019
        columns:
          - name: dispatching_base_num
            description: Base number for the dispatching company
            tests:
              - not_null
```

stg_fhv_tripdata:
```sql
select

    dispatching_base_num,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,
    sr_flag,
    affiliated_base_number

from {{ source('raw', 'fhv_tripdata') }}

where dispatching_base_num is not null
```

**My Result:** **43,261,273**

"I implemented the `stg_fhv_tripdata` model filtering by `dispatching_base_num IS NOT NULL` as requested. While the official answer is **43,244,693**, my execution on the current 2019 FHV Parquet files yielded **43,261,273** records. After performing a data profiling query (`SELECT length(dispatching_base_num), count(*)`), I discovered that my source files only contained 3 actual NULL values, whereas the legacy dataset for this exercise expected 16,580 NULLs. This discrepancy is likely due to an upstream update in the NYC TLC Parquet files. However, the transformation logic is correct and follows all the architectural requirements of the assignment

