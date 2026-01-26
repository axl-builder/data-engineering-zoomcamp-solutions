#### Question 6: Largest tip
**Question:** For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

**Query:**
```sql
SELECT 
    pz."Zone" AS dropoff_zone,
    MAX(hw.tip_amount) AS max_tip
FROM "hw-01-table" hw
JOIN "hw-01-zones" pz ON hw."DOLocationID" = pz."LocationID"
WHERE  pz."Zone" = 'East Harlem North'
AND DATE(hw.lpep_pickup_datetime) > '2025-11-01'
AND DATE(hw.lpep_pickup_datetime) < '2025-11-29'
GROUP BY pz."Zone"
ORDER BY max_tip DESC
LIMIT 1
;
```

**Answer:** `["East Harlem North"	40]`