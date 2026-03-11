import json
from dataclasses import dataclass
import dataclasses


@dataclass
class GreenRide:
    lpep_pickup_datetime: int  # epoch milliseconds
    lpep_dropoff_datetime: int # epoch milliseconds
    PULocationID: int
    DOLocationID: int
    passenger_count: float
    trip_distance: float
    tip_amount: float


def green_ride_from_row(row):
    # Convertimos los timestamps a epoch milliseconds (lo que Flink espera)
    # Pandas read_csv suele leer fechas como strings o objetos datetime
    return GreenRide(
        lpep_pickup_datetime=int(row['lpep_pickup_datetime'].timestamp() * 1000),
        lpep_dropoff_datetime=int(row['lpep_dropoff_datetime'].timestamp() * 1000),
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        passenger_count=float(row['passenger_count']),
        trip_distance=float(row['trip_distance']),
        tip_amount=float(row['tip_amount']),
    )


def green_ride_serializer(ride):
    ride_dict = dataclasses.asdict(ride)
    return json.dumps(ride_dict).encode('utf-8')


def green_ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return GreenRide(**ride_dict)
