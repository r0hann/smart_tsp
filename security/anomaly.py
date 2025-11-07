import os, pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from config import settings

FEATURE_KEYS = ["speed", "distance_m", "lane_queue", "vehicle_type_code"]

def _to_feature_vec(ping: dict) -> np.ndarray:
    vtype = ping.get("vehicle_type", "car")
    vcode = {"car":0, "bus":1, "emergency":2, "truck":3}.get(vtype, 0)
    return np.array([[
        float(ping.get("speed", 0.0)),
        float(ping.get("distance_m", 0.0)),
        float(ping.get("lane_queue", 0.0)),
        float(vcode)
    ]], dtype=float)

class AnomalyGuard:
    def __init__(self, cfg=settings):
        self.cfg = cfg
        self.model = None
        self._load_or_init()

    def _load_or_init(self):
        path = self.cfg.iforest_path
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.model = pickle.load(f)
        else:
            # Train a baseline model on synthetic "normal" data
            rng = np.random.default_rng(self.cfg.seed)
            normal = np.column_stack([
                rng.normal(12, 3, 4000),   # speed m/s
                rng.normal(80, 20, 4000),  # distance_m
                rng.normal(6, 3, 4000),    # lane_queue
                rng.integers(0, 3, 4000)   # vehicle_type_code 0..2
            ])
            self.model = IsolationForest(random_state=self.cfg.seed, contamination=0.02)
            self.model.fit(normal)
            os.makedirs(self.cfg.model_dir, exist_ok=True)
            with open(path, "wb") as f:
                pickle.dump(self.model, f)

    def is_anomalous(self, ping: dict) -> tuple[bool, float]:
        X = _to_feature_vec(ping)
        score = float(self.model.decision_function(X)[0])
        pred = int(self.model.predict(X)[0])  # 1 normal, -1 outlier
        return (pred == -1), score
