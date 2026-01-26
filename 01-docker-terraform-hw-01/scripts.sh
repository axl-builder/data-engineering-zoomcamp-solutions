docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="hw-01" \
  -v hw-01_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  dpage/pgadmin4

uv run python green_tripdata_parquet.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=hw-01 \
  --target-table=hw-01-table 

uv run python zones-dataset.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=hw-01 \
  --target-table=hw-01-zones 

------------------------------------------
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="hw-01" \
  -v hw-01_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name hw-01-database \
  postgres:18

docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4

===============



# Imagen para green_tripdata_parquet
docker build --target green-tripdata -t mi-proyecto:green-tripdata .

# Imagen para zones-dataset
docker build --target zones-dataset -t mi-proyecto:zones-dataset .

===----
docker run -it \
  --network=pg-network \
  mi-proyecto:green-tripdata \
    --pg-user=root \
    --pg-password=root \
    --pg-host=hw-01-database \
    --pg-port=5432 \
    --pg-db=hw-01 \
    --target-table=hw-01-table

docker run -it \
  --network=pg-network \
  mi-proyecto:zones-dataset \
    --pg-user=root \
    --pg-password=root \
    --pg-host=hw-01-database \
    --pg-port=5432 \
    --pg-db=hw-01 \
    --target-table=hw-01-zones



docker run -it --rm\
  --network=pipeline_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --target-table=yellow_taxi_trips