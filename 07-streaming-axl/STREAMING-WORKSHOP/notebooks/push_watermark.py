import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Enviamos un viaje del futuro (2026) para cerrar todas las ventanas de 2025
dummy_ride = {
    "lpep_pickup_datetime": "2026-01-01 00:00:00",
    "lpep_dropoff_datetime": "2026-01-01 00:05:00",
    "PULocationID": 1,
    "DOLocationID": 1,
    "passenger_count": 1.0,
    "trip_distance": 1.0,
    "tip_amount": 0.0,
    "total_amount": 0.0
}

print("Enviando señal de cierre de ventanas (Dummy 2026)...")
producer.send('green-trips', value=dummy_ride)
producer.flush()
print("Señal enviada.")