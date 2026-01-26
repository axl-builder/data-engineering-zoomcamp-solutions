#!/usr/bin/env python
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

dtype = {
    "VendorID": "int32",
    "lpep_pickup_datetime": "datetime64[us]",
    "lpep_dropoff_datetime": "datetime64[us]",
    "store_and_fwd_flag": "str",
    "RatecodeID": "Int64",
    "PULocationID": "int32",
    "DOLocationID": "int32",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "ehail_fee": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "payment_type": "Int64",
    "trip_type": "Int64",
    "congestion_surcharge": "float64",
    "cbd_congestion_fee": "float64"
}

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='hw-01-table', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):

    year = 2025
    month = 11

    batch_size = 100000

    file = f'green_tripdata_{year}-{month:02d}.parquet'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')  # Crea el motor de conexión a tu base de datos PostgreSQL

    pf = pq.ParquetFile(file)  # Abre el archivo Parquet pero NO lo carga en memoria todavía (solo lee metadatos)

    first_batch = next(pf.iter_batches(batch_size=1))  # Extrae solo un pequeño lote (1 fila) para conocer los nombres de las columnas

    df_sample = first_batch.to_pandas()  # Lo convierte a un DataFrame de Pandas para poder manipularlo



    # Aplicar tipos a la muestra y crear la tabla vacía en Postgres

    df_sample = df_sample.astype(dtype)  # Aplica el diccionario de tipos (int32, float64, etc.) para asegurar que coincidan con SQL


    # Crea la tabla en PostgreSQL.
    # head(n=0) significa "solo las columnas, sin datos".
    # if_exists='replace' borra la tabla si ya existía y la crea de nuevo vacía.
    df_sample.head(n=0).to_sql(name=target_table, con=engine, if_exists='replace')


    # Definimos cuántas filas procesar por vez
    

    # Obtenemos el total de filas desde los metadatos del archivo para la barra de progreso
    total_rows = pf.metadata.num_rows

    # Iniciamos 'tqdm' para ver visualmente cuánto falta en Jupyter
    with tqdm(total=total_rows, desc="Cargando datos") as pbar:

        # Este bucle dice: "Dame los siguientes 100,000 registros hasta que se acabe el archivo"
        for batch in pf.iter_batches(batch_size=batch_size):

            # Convierte ese pedazo específico (batch) a un DataFrame de Pandas
            df_chunk = batch.to_pandas()

            # IMPORTANTE: Convierte los tipos de datos de este pedazo antes de subirlo
            df_chunk = df_chunk.astype(dtype)

            # Sube el pedazo a la base de datos.
            # if_exists='append' significa "no borres lo que ya hay, agrégalo al final".
            # index=False evita que se cree una columna extra para los índices de Pandas.
            df_chunk.to_sql(name=target_table, con=engine, if_exists='append', index=False)

            # Mueve la barra de progreso según la cantidad de filas que acabamos de subir
            pbar.update(len(df_chunk))

    pass


if __name__ == '__main__':
    run()
