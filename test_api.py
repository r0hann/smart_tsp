import requests
import time

BASE_URL = "http://127.0.0.1:5000"
TOKEN = "DEMO_TOKEN_123"  # change if you set a custom one in .env

def start_simulation(duration=60):
    url = f"{BASE_URL}/v1/sim/start"
    payload = {"duration_s": duration}
    r = requests.post(url, json=payload)
    print("\n▶️ Start Simulation:", r.status_code, r.json())

def get_state():
    url = f"{BASE_URL}/v1/control/state"
    r = requests.get(url)
    print("\n🚦 Controller State:", r.status_code)
    print(r.json())

def get_metrics():
    url = f"{BASE_URL}/v1/metrics"
    r = requests.get(url)
    print("\n📊 Metrics:", r.status_code)
    print(r.json())

def ingest_vehicle():
    url = f"{BASE_URL}/v1/ingest"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {
        "vehicle_id": "v001",
        "vehicle_type": "car",
        "speed": 12.5,
        "distance_m": 80,
        "approach": "E",
        "lane_queue": 5.0
    }
    r = requests.post(url, headers=headers, json=payload)
    print("\n🚗 Ingest Vehicle:", r.status_code)
    print(r.json())

if __name__ == "__main__":
    start_simulation(30)    # run simulation for 30 seconds
    time.sleep(2)
    get_state()
    get_metrics()
    ingest_vehicle()
