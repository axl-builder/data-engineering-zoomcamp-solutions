#!/bin/bash

# Script to run PostgreSQL in Docker
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v refuerzo:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18


# To connect to the database with UV / psql, use:
# Password: root
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi


# Running Jupyter Notebook
uv run jupyter notebook


# Script de python para digerir datos con click incluido
uv run python ingest_data.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips

# Scripts para correr cliente y base de dato postgresql en una network en comun
# Run PostgreSQL on the network
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v refuerzo:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18

# In another terminal, run pgAdmin on the same network
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data_refuerzo:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4

