import threading, time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from data.generator import random_ping

@dataclass
class SimulationConfig:
    duration_s: int = 60
    rps: float = 5.0  # requests (pings) per second

class Simulator:
    def __init__(self, predictor, anomaly_guard, controller):
        self.predictor = predictor
        self.anomaly_guard = anomaly_guard
        self.controller = controller
        self._thread = None
        self._stop = threading.Event()
        self._metrics = {
            "pings": 0,
            "avg_eta": 0.0,
            "avg_queue": 0.0,
            "throughput": 0,  # vehicles classified as cleared
            "emergency_clear_time_s": 0.0,
        }
        self._etas = deque(maxlen=1000)
        self._queues = deque(maxlen=1000)
        self._approach_stats = {"N":{"queue":0.0,"has_emergency":False},
                                "S":{"queue":0.0,"has_emergency":False},
                                "E":{"queue":0.0,"has_emergency":False},
                                "W":{"queue":0.0,"has_emergency":False}}

    def start(self, cfg: SimulationConfig):
        if self._thread and self._thread.is_alive():
            self._stop.set()
            self._thread.join(timeout=1)
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(cfg,), daemon=True)
        self._thread.start()

    def _run(self, cfg: SimulationConfig):
        t_end = time.time() + cfg.duration_s
        period = 1.0 / max(cfg.rps, 0.1)

        while time.time() < t_end and not self._stop.is_set():
            ping = random_ping()
            self.process_ping(ping)
            time.sleep(period)

    def process_ping(self, ping: dict):
        # Predict
        eta = self.predictor.predict_eta(ping)
        qnext = self.predictor.predict_queue_next(ping)

        # Update metrics
        self._etas.append(eta)
        self._queues.append(qnext)
        self._metrics["pings"] += 1

        appr = ping.get("approach","N")
        vtype = ping.get("vehicle_type","car")
        self._approach_stats[appr]["queue"] = qnext
        self._approach_stats[appr]["has_emergency"] = (vtype == "emergency")

        # Controller update
        self.controller.update_demands(self._approach_stats)

        # Throughput proxy: if this approach has green and eta small, count cleared
        if self.controller.current_green == appr and eta < 5.0:
            self._metrics["throughput"] += 1

        # Emergency clearance time proxy (moving average)
        if vtype == "emergency":
            # heuristic: eta under green approximates clearance time
            self._metrics["emergency_clear_time_s"] = (self._metrics["emergency_clear_time_s"]*0.9 + eta*0.1)

        return {"eta": eta, "queue_next": qnext, "green": self.controller.current_green}

    def metrics(self):
        avg_eta = sum(self._etas)/len(self._etas) if self._etas else 0.0
        avg_queue = sum(self._queues)/len(self._queues) if self._queues else 0.0
        m = dict(self._metrics)
        m["avg_eta"] = round(avg_eta, 3)
        m["avg_queue"] = round(avg_queue, 3)
        return m
