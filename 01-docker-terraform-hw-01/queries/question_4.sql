#### Question 4: Longest trip for each day
**Question:** Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

**Query:**
```sql
SELECT 
    DATE(lpep_pickup_datetime) AS pickup_day,
    MAX(trip_distance) AS max_distance
FROM "hw-01-table"
WHERE trip_distance < 100
GROUP BY pickup_day
ORDER BY max_distance DESC
LIMIT 1;
```

**Answer:** `[2025-11-14]`