import random, uuid
from dataclasses import asdict
from data.schemas import VehiclePing

VEHICLE_TYPES = ["car", "bus", "emergency", "truck"]
APPROACHES = ["N","S","E","W"]

def random_ping(seed: int | None = None) -> dict:
    rng = random.Random(seed)
    vehicle_type = rng.choices(VEHICLE_TYPES, weights=[0.85, 0.09, 0.01, 0.05])[0]
    speed = max(0.0, rng.gauss(12, 3))  # m/s
    distance_m = max(0.0, rng.gauss(120, 40))
    approach = rng.choice(APPROACHES)
    lane_queue = max(0.0, rng.gauss(6, 3))
    vp = VehiclePing(
        vehicle_id=str(uuid.uuid4())[:8],
        vehicle_type=vehicle_type,
        speed=speed,
        distance_m=distance_m,
        approach=approach,
        lane_queue=lane_queue,
    )
    return asdict(vp)
