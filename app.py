from flask import Flask, jsonify, request, render_template
from config import settings
from security.auth import require_token
from security.anomaly import AnomalyGuard
from ml.predictor import Predictor
from control.signal_controller import SignalController
from control.simulator import Simulator, SimulationConfig
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "http://localhost:5173"}}, expose_headers=["Authorization"])

# Singletons
anomaly_guard = AnomalyGuard(settings)
predictor = Predictor(settings)
controller = SignalController()
simulator = Simulator(predictor, anomaly_guard, controller)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/v1/ingest")
@require_token(settings)
def ingest():
    """Ingest a single vehicle telemetry ping."""
    payload = request.get_json(force=True)
    # Anomaly check
    is_anom, score = anomaly_guard.is_anomalous(payload)
    if is_anom:
        return jsonify({"ok": False, "reason": "anomalous", "score": score}), 403

    # Push into simulator pipeline
    result = simulator.process_ping(payload)
    return jsonify({"ok": True, "result": result})

@app.get("/v1/control/state")
def control_state():
    return jsonify(controller.snapshot())

@app.post("/v1/sim/start")
def sim_start():
    cfg = request.get_json(silent=True) or {}
    cfg = SimulationConfig(**cfg)
    simulator.start(cfg)
    return jsonify({"ok": True, "msg": "simulation started", "config": cfg.__dict__})

@app.get("/v1/metrics")
def metrics():
    return jsonify(simulator.metrics())

if __name__ == "__main__":
    app.run(debug=True)
