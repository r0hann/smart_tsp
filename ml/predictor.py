import os, pickle
import numpy as np
from config import settings
from ml.features import vectorize

class Predictor:
    def __init__(self, cfg=settings):
        self.cfg = cfg
        self.eta_model = self._load_model(cfg.eta_model_path)
        self.queue_model = self._load_model(cfg.queue_model_path)

    def _load_model(self, path):
        if not os.path.exists(path):
            # Lazy-train if missing
            from ml.train import main as train_main
            train_main()
        with open(path, "rb") as f:
            return pickle.load(f)

    def predict_eta(self, ping: dict) -> float:
        X = vectorize(ping)
        eta = float(self.eta_model.predict(X)[0])
        return max(0.0, eta)

    def predict_queue_next(self, ping: dict) -> float:
        X = vectorize(ping)
        q = float(self.queue_model.predict(X)[0])
        return max(0.0, q)
