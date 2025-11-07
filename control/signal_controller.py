from collections import defaultdict
import time

APPROACHES = ["N","S","E","W"]

class SignalController:
    def __init__(self):
        self.current_green = "N"  # start with North
        self.last_change_ts = time.time()
        self.min_green_s = 5.0
        self.max_green_s = 45.0
        self.state = {a: {"queue": 0.0, "has_emergency": False, "score": 0.0} for a in APPROACHES}

    def update_demands(self, approach_stats: dict):
        # approach_stats: {approach: {"queue": float, "has_emergency": bool}}
        for a in APPROACHES:
            s = self.state[a]
            s["queue"] = approach_stats.get(a, {}).get("queue", s["queue"])
            s["has_emergency"] = approach_stats.get(a, {}).get("has_emergency", False)

        self._decide()

    def _decide(self):
        now = time.time()
        elapsed = now - self.last_change_ts

        # Hard priority for emergencies
        for a in APPROACHES:
            if self.state[a]["has_emergency"]:
                if self.current_green != a and elapsed >= 2.0:  # allow quick preemption
                    self.current_green = a
                    self.last_change_ts = now
                return

        # Otherwise, heuristic: serve the lane with largest queue score
        if elapsed < self.min_green_s:
            return  # minimum green hold

        scores = {a: self.state[a]["queue"] for a in APPROACHES}
        best = max(scores, key=scores.get)
        if best != self.current_green and elapsed >= self.min_green_s:
            self.current_green = best
            self.last_change_ts = now

        # Force change if overstaying
        if elapsed > self.max_green_s:
            # rotate
            idx = (APPROACHES.index(self.current_green) + 1) % 4
            self.current_green = APPROACHES[idx]
            self.last_change_ts = now

        # store score for debug
        for a in APPROACHES:
            self.state[a]["score"] = scores[a]

    def snapshot(self):
        return {"current_green": self.current_green, "since_s": round(time.time()-self.last_change_ts,1), "state": self.state}
