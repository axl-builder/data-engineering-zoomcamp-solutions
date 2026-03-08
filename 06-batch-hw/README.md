# Module 6 Homework: Spark and PySpark

In this homework, we put into practice the concepts learned about Apache Spark, analyzing the Yellow Taxi dataset for November 2025.

## Setup

1. **Install Spark and PySpark**: Following the course guide for the 2026 cohort.
2. **Download the Dataset**: 
   `wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet`
3. **Download the Zone Lookup**:
   `wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv`

---

### Question 1. Install Spark and PySpark

After installing Spark and creating a local session, what is the output of `spark.version`?

- `3.3.2`
- `3.4.1`
- `3.5.0` ✔
- `4.0.0`

#### Justification:
Spark versioning follows the Apache Software Foundation release cycle. For the 2026 Zoomcamp cohort, **3.5.0** (or a closely related 3.5.x version) is the current stable standard used for the local environment and exercises.

---

### Question 2. Yellow November 2025

Read the November 2025 Yellow data into a Spark Dataframe. Repartition the Dataframe to 4 partitions and save it to parquet. What is the average size of the Parquet files created?

- 6MB
- 25MB ✔
- 75MB
- 100MB

#### Justification:
The source Parquet file for November 2025 is approximately **100MB**. When applying `.repartition(4)`, Spark redistributes the data into four roughly equal parts. Therefore, each resulting partition file is approximately **25MB**.

---

### Question 3. Count records

How many taxi trips were there on the 15th of November? Consider only trips that started on the 15th of November.

- 62,610
- 102,340 ✔
- 162,604
- 225,768

#### Justification:
By filtering the records where the pickup date matches '2025-11-15', the execution returns a total of **102,340**.
**Query:**
```sql
SELECT count(*) 
FROM yellow_tripdata 
WHERE to_date(tpep_pickup_datetime) = '2025-11-15'
```

---

### Question 4. Longest trip
What is the length of the longest trip in the dataset in hours?

22.7

58.2

90.6

134.5 ✔

#### Justification:
By calculating the duration as the difference between dropoff and pickup and converting it to hours, the maximum value is 134.5.
Query:


```sql
SQL
SELECT 
    (unix_timestamp(tpep_dropoff_datetime) - unix_timestamp(tpep_pickup_datetime)) / 3600 AS duration_hours
FROM yellow_tripdata
ORDER BY duration_hours DESC
LIMIT 1
```


---

### Question 5. User Interface
Spark's User Interface which shows the application's dashboard runs on which local port?

80

443

4040 ✔

8080

#### Justification:
By default, Spark launches its web UI (where you can monitor jobs, stages, and tasks) on port 4040. If multiple Spark contexts are running, it will increment to 4041, 4042, etc.

---

### Question 6. Least frequent pickup location zone
Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

Governor's Island/Ellis Island/Liberty Island ✔

Arden Heights

Rikers Island

Jamaica Bay

#### Justification:
After joining the taxi data with the zone lookup table, grouping by Zone and sorting by the count, Governor's Island/Ellis Island/Liberty Island appears with the lowest frequency.
Query:

```sql
SQL
SELECT 
    z.Zone, 
    count(*) as trips
FROM yellow_tripdata t
JOIN taxi_zone_lookup z ON t.PULocationID = z.LocationID
GROUP BY z.Zone
ORDER BY trips ASC
LIMIT 1
```