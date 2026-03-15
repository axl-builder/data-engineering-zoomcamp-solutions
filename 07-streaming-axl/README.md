Data Engineering Zoomcamp 2026 - Module 7: Stream Processing (Homework)
This repository contains the solution for the Stream Processing homework, using Redpanda as the message broker, PyFlink for stream processing, and PostgreSQL as the sink.

Quiz Questions
Question 1. Redpanda version
What version of Redpanda are you running?

v25.3.9 ✓

Justification:
Executed rpk version inside the container:

Bash
docker exec -it 07-streaming-axl-redpanda-1 rpk version
Output:
rpk version: v25.3.9 (rev 836b4a3)

Question 2. Sending data to Redpanda
How long did it take to send the data?

10 seconds

60 seconds ✓ (Approx. 77.85s in local environment)

120 seconds

300 seconds

Justification:
Using a Python producer with KafkaProducer and the green_tripdata_2025-10.parquet dataset.
Input (Producer Logic):

Python
import pandas as pd
import time
from kafka import KafkaProducer

df = pd.read_parquet("green_tripdata_2025-10.parquet")
producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda v: json.dumps(v).encode('utf-8'))

t0 = time.time()
for row in df.to_dict(orient='records'):
    producer.send('green-trips', value=row)
producer.flush()
t1 = time.time()
print(f'took {(t1 - t0):.2f} seconds')
Output: took 77.85 seconds

Question 3. Consumer - trip distance
How many trips have trip_distance > 5?

6506

7506

8506 ✓

9506

Justification:
Using a Kafka consumer to iterate through the green-trips topic from the earliest offset.
Input:

Python
consumer = KafkaConsumer('green-trips', bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest', consumer_timeout_ms=10000)
count = sum(1 for msg in consumer if msg.value['trip_distance'] > 5.0)
print(f"Total: {count}")
Output: Total de viajes con distancia > 5.0: 8506

Question 4. Tumbling window - pickup location
Which PULocationID had the most trips in a single 5-minute window?

42

74 ✓

75

166

Justification:
Flink Job using a TUMBLE window of 5 minutes.
SQL Query:

SQL
SELECT PULocationID, num_trips
FROM q4_pickup_stats
ORDER BY num_trips DESC
LIMIT 1;
Result: PULocationID: 74

Question 5. Session window - longest streak
How many trips were in the longest session?

12

31 ✓

51

81

Justification:
Flink Job using a SESSION window with a 5-minute gap. To close the final windows of the 2025 dataset, a "dummy" record with a 2026 timestamp was sent to advance the watermark.
SQL Query:

SQL
SELECT num_trips FROM q5_session_stats ORDER BY num_trips DESC LIMIT 1;
Result: 31 (Note: Duplicates in the stream might inflate this value, but 31 is the expected result for the clean dataset).

Question 6. Tumbling window - largest tip
Which hour had the highest total tip amount?

2025-10-01 18:00:00

2025-10-16 18:00:00 ✓

2025-10-22 08:00:00

2025-10-30 16:00:00

Justification:
Flink Job using a TUMBLE window of 1 hour for SUM(tip_amount).
Input/Output:

SQL
postgres@localhost:postgres> SELECT window_start, total_tip_amount
 FROM q6_tip_stats
 ORDER BY total_tip_amount DESC
 LIMIT 1;
+---------------------+-------------------+
| window_start        | total_tip_amount  |
|---------------------+-------------------|
| 2025-10-16 18:00:00 | 503.1599999999999 |
+---------------------+-------------------+