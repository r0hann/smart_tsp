import numpy as np

VTYPE_MAP = {"car":0, "bus":1, "emergency":2, "truck":3}
APPROACH_MAP = {"N":0, "S":1, "E":2, "W":3}

def vectorize(ping: dict) -> np.ndarray:
    vtype = VTYPE_MAP.get(ping.get("vehicle_type","car"), 0)
    appr = APPROACH_MAP.get(ping.get("approach","N"), 0)
    return np.array([[
        float(ping.get("speed",0.0)),
        float(ping.get("distance_m",0.0)),
        float(ping.get("lane_queue",0.0)),
        float(vtype),
        float(appr),
    ]], dtype=float)
