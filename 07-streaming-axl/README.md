# 🚖 Module 07 Homework: Streaming with PyFlink and Redpanda

Hands-on stream processing with **Apache Flink** and **Redpanda** (a Kafka-compatible event store), analyzing the Green Taxi dataset for October 2019.

---

## ⚙️ Setup

### Infrastructure

Start the environment using the provided `docker-compose.yml` (includes Redpanda, Flink Job Manager, Flink Task Manager, and Postgres):

```bash
docker-compose up -d
```

### Dataset

Green Taxi — October 2019 data.

### Database Tables

Create the landing zone in Postgres:

```sql
CREATE TABLE processed_events (
    test_data INTEGER,
    event_timestamp TIMESTAMP
);

CREATE TABLE processed_events_aggregated (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    pu_id INTEGER,
    do_id INTEGER,
    num_trips INTEGER,
    PRIMARY KEY (window_start, pu_id, do_id)
);
```

---

## ❓ Questions & Answers

### Question 1 — Redpanda Version

> What is the version of Redpanda based on the output of `rpk version`?

- **✅ v25.3.9 - 836b4a36ef6d5121edbb1e68f0f673c2a8a244e2**

**Justification:** By executing the command inside the running container, we retrieve the specific build version currently deployed in the stack.

```bash
docker compose exec redpanda rpk version
```

---

### Question 2 — Creating a Topic

> What is the output of the command for creating a topic named `green-trips`?


- **✅ TOPIC green-trips OK**


**Justification:** Using the `rpk topic create` utility, Redpanda confirms the creation of the topic and its readiness status.

```bash
docker compose exec redpanda rpk topic create green-trips
```

---

### Question 3 — Connecting to the Kafka Server

> Given that you can connect using the `kafka-python` library, what does `producer.bootstrap_connected()` return?

- **✅ True**


**Justification:**
```bash
uv run python test_connection.py 
```

---

### Question 4 — Sending the Trip Data

> How long did it take to send the entire dataset and flush the producer?


- **✅ 103.01 seconds**


---

### Question 5 — Sessionization Window

> Which pickup and dropoff location pair has the longest unbroken streak of taxi trips (highest number of trips in a single session window)?


- ****PU 75, DO 74** ( **364** trips).**


**Justification:** 

```sql
SELECT pu_id, do_id, num_trips
FROM processed_events_aggregated
ORDER BY num_trips DESC
LIMIT 1;
```
| pu_id | do_id | num_trips |

|-------+-------+-----------|

| 75    | 74    | 364       |
---
