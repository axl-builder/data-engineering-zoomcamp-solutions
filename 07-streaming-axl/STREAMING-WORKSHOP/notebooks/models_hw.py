import json
from dataclasses import dataclass
import dataclasses


@dataclass
class GreenRide:
    lpep_pickup_datetime: str  # epoch milliseconds
    lpep_dropoff_datetime: str # epoch milliseconds
    PULocationID: int
    DOLocationID: int
    passenger_count: float
    trip_distance: float
    tip_amount: float
    total_amount: float
 

def green_ride_from_row(row):
    # Convertimos los timestamps a epoch milliseconds (lo que Flink espera)
    # Pandas read_csv suele leer fechas como strings o objetos datetime
    return GreenRide(
        lpep_pickup_datetime=row['lpep_pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
        lpep_dropoff_datetime=row['lpep_dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        passenger_count=float(row['passenger_count']),
        trip_distance=float(row['trip_distance']),
        tip_amount=float(row['tip_amount']),
        total_amount=float(row['total_amount']),
    )


def green_ride_serializer(ride):
    return json.dumps(dataclasses.asdict(ride)).encode('utf-8')


def green_ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return GreenRide(**ride_dict)
