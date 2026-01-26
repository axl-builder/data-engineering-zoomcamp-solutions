# Data Engineering Zoomcamp 2025/2026 - Module 01 Homework

**Course:** [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by DataTalks.Club  
**Module:** 01 - Docker & Terraform  
**Student:** Axel Leonel Lifschitz  
**Date:** 26/01/2026

---

## 📋 Project Description

This repository contains the solution to Module 01 homework of the Data Engineering Zoomcamp, covering:

- 🐳 Containerization with Docker
- 🗄️ PostgreSQL configuration
- 📊 NYC Taxi data ingestion (Green Taxi Trip Records)
- 🔍 SQL queries for data analysis
- ☁️ Infrastructure as Code with Terraform and GCP

---

## 🛠️ Technologies Used

- **Python 3.13**
- **Docker & Docker Compose**
- **PostgreSQL 13**
- **pgAdmin 4**
- **uv** (Python dependency manager)
- **SQLAlchemy** (Python ORM)
- **Pandas & PyArrow** (data manipulation)
- **Terraform** (Infrastructure as Code)
- **Google Cloud Platform (GCP)**

---

## 📂 Project Structure

```
hw-01/
├── Dockerfile                      # Multi-stage build for both scripts
├── docker-compose.yaml              # Service orchestration (PostgreSQL + pgAdmin)
├── pyproject.toml                  # Project dependencies (uv)
├── uv.lock                         # Dependencies lock file
├── .python-version                 # Python version
├── green_tripdata_parquet.py       # Green Taxi data ingestion script
├── zones-dataset.py                # NYC zones ingestion script
├── terraform/                      # Terraform configuration
│   ├── main.tf
│   └── variables.tf
├── queries/                        # SQL queries for homework
│   ├── question_3.sql
│   ├── question_4.sql
│   ├── question_5.sql
│   └── question_6.sql
└── README.md                       # This file
```

---

## 🚀 Setup and Installation

### Prerequisites

- Docker and Docker Compose installed
- Python 3.13+
- uv installed (`pip install uv`)
- GCP account (for Terraform section)

### 1. Levantar la infraestructura
docker-compose up -d

### 2. Construir la imagen única de ingesta
docker build -t taxi-ingest-image:latest .

### 3. Ingestar las Zonas (Ejecutando un script específico)
docker run -it --network=hw-01_default \
  taxi-ingest-image:latest \
    uv run zones-dataset.py \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=hw-01-database \
    --pg-db=hw-01 \
    --target-table=zones

### 4. Ingestar los Viajes (Ejecutando el otro script)
# Nota: Montamos el volumen para que vea el archivo parquet local
docker run -it --network=hw-01_default \
  -v $(pwd):/app \
  taxi-ingest-image:latest \
    uv run green_tripdata_parquet.py \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=hw-01-database \
    --pg-db=hw-01 \
    --target-table=green_taxi_data



## 📝 Homework Questions

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entry point `bash` to interact with the container.

What's the version of `pip` in the image?

- 25.3   ✔
- 24.3.1
- 24.2.1
- 23.3.1

###### Justification:
First, we create a container with bash access, using `python:3.13-slim` as the base image:

```bash
Docker run -it \
    --rm \
    --entrypoint=bash \
    python:3.13-slim
```

Once inside, we execute the following command within the bash session:
```bash
pip --version
```

output:
	pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)


---
## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgAdmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433 
- localhost:5432
- db:5433
- postgres:5432 ✔
- db:5432 ✔

###### Justification:
In Docker Compose, containers communicate with each other using the **service name** (`db`) or the **container_name** (`postgres`) as the hostname, thanks to Docker's built-in DNS. Since this is internal communication within the same network, pgAdmin must use the container's **internal port** (`5432`) instead of the port mapped to the host (`5433`).

### Section: Docker & SQL

#### Question 3: Counting short trips
**Question:** For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

**Query:**
```sql
SELECT COUNT(*)
FROM "hw-01-table"
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

**Answer:** `[8007]`

---

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

---

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

---

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
AND DATE(hw.lpep_pickup_datetime) >= '2025-11-01'
AND DATE(hw.lpep_pickup_datetime) < '2025-12-01'
GROUP BY pz."Zone"
ORDER BY max_tip DESC
LIMIT 1
;
```

**Answer:** `["East Harlem North"	40]`

---

### Section: Terraform

#### Question 7: TTerraform Setup & GCP Provisioning
**Question:** Question: Configure and execute Terraform manifests to provision a Google Cloud Storage (GCS) bucket and a BigQuery dataset using the standard course structure.

**Steps completed:**

Environment Setup: Installed Terraform CLI and configured the Google Cloud provider. Authenticated via terminal using:

Bash
gcloud auth application-default login
Manifest Configuration: * Modified variables.tf to define the project, location, and names for the infrastructure, using the default attribute for project-specific values.

Updated main.tf to reference these variables, ensuring the google_storage_bucket and google_bigquery_dataset resources are correctly linked to the GCP Project ID.

Infrastructure Lifecycle (CLI):

Bash
### Prepare the directory and install GCS/BigQuery providers
terraform init

### Preview the changes to be made in the GCP Project
terraform plan

### Provision the resources
terraform apply
Resources created:

GCS Bucket: [terraform-demo-terra-bucket_hw_01]

BigQuery Dataset: [demo_dataset_hw_01]

---

## 📊 Results and Learnings

### Key concepts learned:

1. **Containerization:** Packaging applications with all their dependencies
2. **Docker Networks:** Communication between containers using `--network`
3. **PostgreSQL:** Setup and management of relational databases
4. **SQL:** Data analysis with complex queries (JOINs, aggregations)
5. **IaC with Terraform:** Automated provisioning of cloud infrastructure
6. **Data Pipelines:** Automated ingestion of public datasets

### Challenges overcome:

- Configuration of multi-stage Docker builds with `uv`
- Resolving dependency issues (sqlalchemy not found)
- Understanding the difference between `uv run` and venv executables
- Build process optimization to avoid reinstallations

---

## 🔗 Useful Links

- [Official course repository](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- [Original homework](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2025/01-docker-terraform/homework.md)
- [NYC TLC Trip Record Data](https://github.com/DataTalksClub/nyc-tlc-data)
- [DataTalks.Club Slack](https://datatalks.club/slack.html)

---

## 📧 Contact

**LinkedIn:** [\[your-profile\]](https://www.linkedin.com/in/axellifschitz/)  
**GitHub:** axl-builder  
**Email:** axelleonellifschitz@gmail.com

---

## 🙏 Acknowledgments

Thanks to [Alexey Grigorev](https://github.com/alexeygrigorev) and the entire [DataTalks.Club](https://datatalks.club/) team for this free, high-quality course.

---

## 📄 License

This project is part of the course homework and is available for educational purposes.


