# Module 3 Homework: Data Warehousing & BigQuery

## Data

For this homework we will be using the Yellow Taxi Trip Records for January 2024 - June 2024 (not the entire year of data).

Parquet Files are available from the New York City Taxi Data found here:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Loading the data

You can use the following scripts to load the data into your GCS bucket:

- Python script: [load_yellow_taxi_data.py](./load_yellow_taxi_data.py)
- Jupyter notebook with DLT: [DLT_upload_to_GCP.ipynb](./DLT_upload_to_GCP.ipynb)

You will need to generate a Service Account with GCS Admin privileges or be authenticated with the Google SDK, and update the bucket name in the script.

If you are using orchestration tools such as Kestra, Mage, Airflow, or Prefect, do not load the data into BigQuery using the orchestrator.

Make sure that all 6 files show in your GCS bucket before beginning.

Note: You will need to use the PARQUET option when creating an external table.


## BigQuery Setup

Create an external table using the Yellow Taxi Trip Records. 

Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). 



## Question 1. Counting records

What is count of records for the 2024 Yellow Taxi Data?
- 65,623
- 840,402
- 20,332,093 ✅
- 85,431,289

##### Justification:
```sql
SELECT count(*)

FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned`;
```

## Question 2. Data read estimation

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
 
What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?

- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
- 0 MB for the External Table and 155.12 MB for the Materialized Table ✅
- 2.14 GB for the External Table and 0MB for the Materialized Table
- 0 MB for the External Table and 0MB for the Materialized Table

##### Justification:
```sql
SELECT COUNT(DISTINCT PULocationID) FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata`;
```

```sql
SELECT COUNT(DISTINCT PULocationID) FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned`;
```

## Question 3. Understanding columnar storage

Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.

Why are the estimated number of Bytes different?
- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires ✅
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
- BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, 
doubling the estimated bytes processed.
- BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
- When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

##### Justification:
```sql
SELECT PULocationID FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned`;
```

```sql
SELECT PULocationID, DOLocationID FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned`;
```

## Question 4. Counting zero fare trips

How many records have a fare_amount of 0?
- 128,210
- 546,578
- 20,188,016
- 8,333 ✅

##### Justification:
```sql
SELECT COUNT(*) FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned` WHERE fare_amount = 0;
```

## Question 5. Partitioning and clustering

What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)

- Partition by tpep_dropoff_datetime and Cluster on VendorID ✅
- Cluster on by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on tpep_dropoff_datetime Partition by VendorID
- Partition by tpep_dropoff_datetime and Partition by VendorID

##### Justification:
```sql
CREATE OR REPLACE TABLE `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_optimized` PARTITION BY DATE(tpep_dropoff_datetime) CLUSTER BY VendorID AS SELECT * FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.external_yellow_tripdata`;
```

- **Partitioning (The "Big Filter"):** By partitioning the table on a `DATE` or `TIMESTAMP` column (like `tpep_dropoff_datetime`), BigQuery physically divides the data into distinct segments. When you run a query with a date filter, BigQuery performs **"partition pruning"**, meaning it ignores all data outside that date range. This drastically reduces the number of bytes scanned and, consequently, the cost.
    
- **Clustering (The "Internal Sort"):** Within each partition, clustering sorts the data based on the `VendorID`. Since the requirement is to order results by this column, clustering ensures the data is already pre-sorted on disk. This makes sorting operations much faster and further optimizes queries that filter by specific Vendors.
- 
## Question 6. Partition benefits

Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)


Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? 


Choose the answer which most closely matches.
 

- 12.47 MB for non-partitioned table and 326.42 MB for the partitioned table
- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table ✅
- 5.87 MB for non-partitioned table and 0 MB for the partitioned table
- 310.31 MB for non-partitioned table and 285.64 MB for the partitioned table

##### Justification:
```sql
SELECT DISTINCT VendorID FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_non_partitioned` WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

```sql
SELECT DISTINCT VendorID FROM `NOMBRE_DE_TU_PROYECTO.zoomcamp.yellow_tripdata_2024_optimized` WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```
## Question 7. External table storage

Where is the data stored in the External Table you created?

- Big Query
- Container Registry
- GCP Bucket ✅
- Big Table

##### Justification:
An **External Table** in BigQuery is a table where the metadata (schema and definition) resides in BigQuery, but the actual data remains in an external source—in this case, a **Google Cloud Storage (GCP) Bucket**.

## Question 8. Clustering best practices

It is best practice in Big Query to always cluster your data:
- True
- False ✅

##### Justification:
While clustering is a powerful optimization technique, it is **not** a best practice to apply it universally to every table. The decision to use clustering should be based on the specific **query patterns** and the **size of the dataset**.

Clustering is most effective for:

- **Large datasets** (typically over 10 MB) where scanning the entire table is costly.
    
- **Columns with high cardinality** that are frequently used in filters (`WHERE`) or as sorting keys (`ORDER BY`).
    

Applying clustering to very small tables or to columns that are never used for filtering adds unnecessary overhead to the write operations without providing any tangible performance or cost benefits. Therefore, a selective and strategic approach to clustering is preferred over a "one-size-fits-all" implementation.

## Question 9. Understanding table scans

No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

##### Justification:
When you execute a `SELECT COUNT(*)` on a **materialized (native) table**, BigQuery does not need to scan the actual data blocks. Instead, it retrieves the row count directly from the **table's metadata**.

BigQuery stores pre-computed statistics for every native table, including the total number of rows, which are updated whenever data is loaded or modified. Since no columns are actually read and no data is processed by the execution engine, the estimated and actual bytes processed will be **0**. This highlights the efficiency of BigQuery’s metadata management system compared to traditional databases or external tables, where a full scan might be required to determine the total record count.