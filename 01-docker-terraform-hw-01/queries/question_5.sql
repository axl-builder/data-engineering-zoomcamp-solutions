#### Question 5: Biggest pickup zone
**Question:** Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

**Query:**
```sql
SELECT 
    pz."Zone" AS dropoff_zone,
    SUM(hw.tip_amount) AS total_tip
FROM "hw-01-table" hw
JOIN "hw-01-zones" pz ON hw."PULocationID" = pz."LocationID"
WHERE  DATE(hw.lpep_pickup_datetime) = '2025-11-18'
GROUP BY pz."Zone"
ORDER BY total_tip DESC
LIMIT 3
;
```

**Answer:** `["East Harlem North"	1187.1000000000001]`