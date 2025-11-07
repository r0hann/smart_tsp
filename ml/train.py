import os, pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from config import settings
from data.generator import random_ping
from ml.features import vectorize

def synth_train_data(n=4000, seed=42):
    rng = np.random.default_rng(seed)
    X, y_eta, y_queue = [], [], []
    for i in range(n):
        ping = random_ping()
        x = vectorize(ping)[0]
        # Synthetic ground-truth (simple physics + noise)
        speed = ping["speed"]
        dist = ping["distance_m"]
        base_eta = dist / max(speed, 0.1)
        # emergency has lower expected delay (priority)
        vtype_bonus = {"car": 8, "bus": 5, "emergency": 1, "truck": 10}[ping["vehicle_type"]]
        eta = base_eta + 0.5*ping["lane_queue"] + vtype_bonus + rng.normal(0, 3)
        qnext = max(0.0, ping["lane_queue"] + rng.normal(0, 1.0) + (1 if speed < 3 else -0.5))
        X.append(x); y_eta.append(eta); y_queue.append(qnext)
    return np.array(X), np.array(y_eta), np.array(y_queue)

def _try_import():
    try:
        from xgboost import XGBRegressor
    except Exception:
        XGBRegressor = None
    try:
        from lightgbm import LGBMRegressor
    except Exception:
        LGBMRegressor = None
    return XGBRegressor, LGBMRegressor

def main():
    os.makedirs(settings.model_dir, exist_ok=True)
    X, y_eta, y_queue = synth_train_data(seed=settings.seed)

    XGBRegressor, LGBMRegressor = _try_import()

    # ETA model
    if XGBRegressor:
        eta_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.9, colsample_bytree=0.9, random_state=settings.seed)
    else:
        eta_model = RandomForestRegressor(n_estimators=200, random_state=settings.seed)
    eta_model.fit(X, y_eta)

    # Queue model
    if LGBMRegressor:
        queue_model = LGBMRegressor(n_estimators=300, max_depth=-1, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=settings.seed)
    else:
        queue_model = RandomForestRegressor(n_estimators=200, random_state=settings.seed)
    queue_model.fit(X, y_queue)

    with open(settings.eta_model_path, "wb") as f:
        pickle.dump(eta_model, f)
    with open(settings.queue_model_path, "wb") as f:
        pickle.dump(queue_model, f)
    print("Models saved:", settings.eta_model_path, settings.queue_model_path)

if __name__ == "__main__":
    main()
