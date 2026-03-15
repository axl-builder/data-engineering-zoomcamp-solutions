import pandas as pd
import time
from kafka import KafkaProducer
from models_hw import green_ride_from_row, green_ride_serializer

# 1. Leer Parquet Local (2025-10)
# Asegurate de que el archivo esté en la misma carpeta
file_path = "green_tripdata_2025-10.parquet"
df = pd.read_parquet(file_path)

# 2. Filtrar columnas necesarias
columns = [
    'lpep_pickup_datetime', 'lpep_dropoff_datetime',
    'PULocationID', 'DOLocationID', 'passenger_count',
    'trip_distance', 'tip_amount', 'total_amount'
]
df = df[columns]

# 3. Setup del Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=green_ride_serializer
)

topic_name = 'green-trips'

print(f"Iniciando envío de {len(df)} registros...")
t0 = time.time()

# 4. El loop masivo optimizado
# Usamos to_dict para que el acceso sea un poco más rápido que iterrows
for row in df.to_dict(orient='records'):
    ride = green_ride_from_row(row)
    producer.send(topic_name, value=ride)

producer.flush()
t1 = time.time()

print(f'took {(t1 - t0):.2f} seconds')