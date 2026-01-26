#### Question 3: Counting short trips
**Question:** For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

**Query:**
```sql
SELECT COUNT(*)
FROM hw-01-table
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

**Answer:** `[8007]`