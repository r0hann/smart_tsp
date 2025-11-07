# 🚦 Smart TSP — Smart Traffic Signal Priority System

An intelligent traffic signal simulation platform that dynamically optimizes signal timing based on live vehicle telemetry, using a **Python (Flask)** backend and a **React + Tailwind** frontend.

---

## 📖 Overview

**Smart TSP** simulates how adaptive traffic signals respond to real-time vehicle data.  
It demonstrates the concept of **Traffic Signal Priority (TSP)** — where buses and emergency vehicles are given higher priority at intersections to reduce delay and congestion.

The project consists of:
- 🧠 **Backend (Flask):** Simulates vehicle telemetry, traffic controller logic, and provides REST API endpoints.  
- 💻 **Frontend (React + Vite + Tailwind):** Visual dashboard to control the simulation, monitor live metrics, and visualize queues per direction.

---

## 🏗️ Project Structure

```
smart_tsp/
├── app.py                  # Flask application entrypoint
├── simulator/              # Simulation engine (predictor, controller, anomaly guard)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── frontend/               # React + Vite dashboard
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    ├── vite.config.js
    └── ...
```

---

## ⚙️ Backend Setup (Flask)

### 1️⃣ Create a virtual environment
```bash
cd smart_tsp
python -m venv .venv
source .venv/bin/activate     # On macOS/Linux
# .venv\Scripts\activate.bat  # On Windows
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Flask server
```bash
python app.py
```

The API runs on:
```
http://127.0.0.1:5000
```

---

## 💻 Frontend Setup (React + Vite)

### 1️⃣ Move into the frontend directory
```bash
cd frontend
```

### 2️⃣ Install dependencies
```bash
npm install
```

### 3️⃣ Start the development server
```bash
npm run dev
```

The dashboard will be available at:
```
http://localhost:5173
```

### 4️⃣ Connect Backend + Frontend
If you see a CORS issue, ensure Flask includes:
```python
from flask_cors import CORS
CORS(app)
```
or configure a proxy in `vite.config.js`.

---

## 🚀 How to Use

### ▶️ Start Simulation
Click **“Start 60s sim”** to begin a 60-second run.  
This triggers the backend simulation via `/v1/sim/start`.

### 📡 Send Manual Ping
Click **“Send manual ping”** to send one simulated vehicle update to the backend (`/v1/ingest`).

### 📊 Live Metrics
- **Average ETA:** Average travel time for all vehicles (seconds).  
- **Average Queue:** Average number of vehicles waiting per approach.  
- **Pings:** Total telemetry updates received.  
- **Traffic Status:** Interprets queue length:

| Range | Label | Description |
|--------|--------|-------------|
| 0–3 | Light traffic | Smooth flow |
| 4–6 | Moderate traffic | Some delay |
| 7–11 | Heavy congestion | Needs optimization |
| ≥12 | Severe congestion | Critical |

### 🚦 Controller Visualization
Shows the current **green direction (N/S/E/W)** and per-lane queue bars.  
Emergency vehicles are highlighted with a red **EMG** badge.

### 🧾 Logs
Displays raw backend responses and events for debugging and transparency.

---

## 🧠 Technical Highlights

- Modular backend built on **Flask + Flask-CORS**  
- Interactive React frontend with **TailwindCSS**  
- Real-time updates via periodic API polling  
- Visualization of queue dynamics and controller state  
- Extensible simulation logic for research and demos

---

## 🔧 Future Enhancements

- 📈 Line charts for queue and ETA trends  
- 🧩 Multi-intersection simulation  
- 🤖 Reinforcement learning integration for adaptive signals  
- 💾 Persistent data logging (SQLite/PostgreSQL)  
- 🚗 Real-world GPS/IoT telemetry integration  

---

## 🪪 License

This project is open-source under the **MIT License**.
****
