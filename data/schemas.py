from dataclasses import dataclass

@dataclass
class VehiclePing:
    vehicle_id: str
    vehicle_type: str  # car | bus | emergency | truck
    speed: float       # m/s
    distance_m: float  # meters to stop-line
    approach: str      # N|S|E|W
    lane_queue: float  # vehicles observed in lane
