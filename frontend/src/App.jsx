import React, { useState, useEffect, useRef } from 'react'
import { startSim, getState, getMetrics, ingestPing } from './api'

function QueueBar({ label, value, max, isGreen, emergency }) {
  const pct = Math.min(100, Math.round((value / Math.max(1, max)) * 100))
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between text-sm">
        <div className="font-medium">{label}{emergency ? <span className="ml-2 px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded">EMG</span> : null}</div>
        <div className="text-xs text-slate-500">{value.toFixed(2)}</div>
      </div>
      <div className={`w-full h-3 mt-1 rounded bg-slate-100 overflow-hidden ${isGreen ? 'ring-2 ring-green-200' : ''}`}>
        <div
          style={{ width: `${pct}%` }}
          className={`h-full ${isGreen ? 'bg-green-500' : 'bg-sky-500'}`}
        />
      </div>
    </div>
  )
}

function getTrafficStatus(avgQueue) {
  if (avgQueue == null) return { label: '—', color: 'text-slate-400', description: '' }

  if (avgQueue < 3)
    return { label: 'Light traffic', color: 'text-green-600', description: 'Smooth flow' }

  if (avgQueue < 7)
    return { label: 'Moderate traffic', color: 'text-yellow-600', description: 'Some delay' }

  if (avgQueue < 12)
    return { label: 'Heavy congestion', color: 'text-orange-600', description: 'Needs optimization' }

  return { label: 'Severe congestion', color: 'text-red-600', description: 'Critical' }
}


export default function App() {
  const [state, setState] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [running, setRunning] = useState(false)
  const [timeLeft, setTimeLeft] = useState(0)
  const [simDuration, setSimDuration] = useState(60)
  const [token, setToken] = useState('DEMO_TOKEN_123')
  const [log, setLog] = useState([])
  const [toast, setToast] = useState(null)

  // refs to avoid stale closures
  const timeRef = useRef(timeLeft); timeRef.current = timeLeft;
  const runningRef = useRef(running); runningRef.current = running;

  // Poll backend for state/metrics every 2.5s
  useEffect(() => {
    let t = setInterval(async () => {
      try {
        const s = await getState()
        setState(s)
        const m = await getMetrics()
        setMetrics(m)
      } catch (err) {
        // ignore
      }
    }, 2500)
    return () => clearInterval(t)
  }, [])

  // Countdown timer effect
  useEffect(() => {
    if (!running) return
    if (timeLeft <= 0) {
      setRunning(false)
      setToast('Simulation finished')
      setTimeout(() => setToast(null), 3000)
      return
    }
    const id = setInterval(() => {
      if (timeRef.current <= 1) {
        setTimeLeft(0)
        clearInterval(id)
        setRunning(false)
        setToast('Simulation finished')
        setTimeout(() => setToast(null), 3000)
      } else {
        setTimeLeft(prev => prev - 1)
      }
    }, 1000)
    return () => clearInterval(id)
  }, [running, timeLeft])

  async function handleStart() {
    try {
      const r = await startSim({ duration_s: 60, rps: 5 })
      setLog(l => [...l, JSON.stringify(r)])
      const dur = (r && r.config && r.config.duration_s) ? Number(r.config.duration_s) : 60
      setSimDuration(dur)
      setTimeLeft(dur)
      setRunning(true)
    } catch (err) {
      setLog(l => [...l, 'startSim error: ' + (err.message || err)])
    }
  }

  async function handleIngest() {
    const ping = {
      vehicle_id: 'manual-' + Math.random().toString(36).slice(2, 8),
      vehicle_type: 'bus',
      speed: 8 + Math.random() * 10,
      distance_m: 50 + Math.random() * 120,
      approach: ['N', 'S', 'E', 'W'][Math.floor(Math.random() * 4)],
      lane_queue: Math.round(2 + Math.random() * 8)
    }

    try {
      const r = await ingestPing(ping, token)

      // ✅ Build a human-readable description
      const description = `🚗 Vehicle ${ping.vehicle_id} (${ping.vehicle_type.toUpperCase()})
    → Approach: ${ping.approach}
    → Speed: ${ping.speed.toFixed(1)} m/s
    → Distance: ${ping.distance_m.toFixed(1)} m
    → Queue: ${ping.lane_queue}
    ✅ Controller Response: ${r.ok ? 'Accepted' : 'Error'}
    ${r.message ? '📡 ' + r.message : ''}`

      // ✅ Add both raw and readable versions to the log
      setLog(l => [
        ...l,
        description,
        '📦 Raw response: ' + JSON.stringify(r)
      ])
    } catch (err) {
      setLog(l => [...l, '❌ Error sending ping: ' + err.message])
    }
  }


  // helper for visuals
  const approachOrder = ['N', 'S', 'E', 'W']
  let queueMax = 10
  if (state && state.state) {
    // find a reasonable max for bar scaling (avoid tiny bars)
    const queues = approachOrder.map(a => (state.state[a]?.queue ?? 0))
    queueMax = Math.max(6, ...queues, queueMax)
  }

  const progressPct = simDuration > 0 ? Math.round(((simDuration - timeLeft) / simDuration) * 100) : 0

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-4xl font-extrabold mb-6">Smart TSP — Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Simulation card */}
        <div className="p-4 rounded-lg bg-white shadow">
          <h3 className="font-medium mb-3">Simulation</h3>

          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={handleStart}
              disabled={running}
              className="px-4 py-2 rounded bg-sky-600 disabled:text-slate-500 disabled:opacity-60"
            >
              Start 60s sim
            </button>

            <button
              onClick={handleIngest}
              className="px-4 py-2 rounded border"
            >
              Send manual ping
            </button>

          </div>
          <div className="ml-auto text-sm text-slate-700">
            <div className="font-medium">Time left:</div>
            <div className="text-lg">{running ? `${timeLeft}s` : '—'}</div>
          </div>

          {/* progress bar */}
          <div className="mb-3">
            <div className="h-3 bg-slate-100 rounded overflow-hidden">
              <div style={{ width: `${progressPct}%` }} className="h-full bg-emerald-500 transition-all duration-300"></div>
            </div>
            <div className="text-xs text-slate-500 mt-1">{progressPct}%</div>
          </div>

          <div className="mt-6 text-sm text-slate-500">Simulation controls and quick actions.</div>
        </div>

        {/* Metrics card */}
        <div className="p-4 rounded-lg bg-white shadow">
          <h3 className="font-medium mb-3">Metrics</h3>
          {metrics ? (
            <div>
              <div className="mb-4">
                <div className="flex justify-between text-sm">
                  <div>Average ETA</div>
                  <div className="font-medium">{metrics.avg_eta?.toFixed(2) ?? '—'}s</div>
                </div>
                <div className="h-3 bg-slate-100 rounded overflow-hidden mt-1">
                  <div style={{ width: `${Math.min(100, (metrics.avg_eta / 60) * 100)}%` }} className="h-full bg-indigo-500"></div>
                </div>
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm">
                  <div>Average Queue</div>
                  <div className="font-medium">{metrics.avg_queue?.toFixed(2) ?? '—'}</div>
                </div>
                <div className="h-3 bg-slate-100 rounded overflow-hidden mt-1">
                  <div
                    style={{ width: `${Math.min(100, (metrics.avg_queue / queueMax) * 100)}%` }}
                    className="h-full bg-yellow-500"
                  ></div>
                </div>

                {/* NEW STATUS INDICATOR */}
                {(() => {
                  const status = getTrafficStatus(metrics.avg_queue)
                  return (
                    <div className={`mt-1 text-sm font-medium ${status.color}`}>
                      {status.label} — {status.description}
                    </div>
                  )
                })()}
              </div>


              <div>
                <div className="flex justify-between text-sm">
                  <div>Pings</div>
                  <div className="font-medium">{metrics.pings ?? 0}</div>
                </div>
                <div className="text-xs text-slate-400 mt-2">Throughput: {metrics.throughput ?? 0}</div>
              </div>
            </div>
          ) : (
            <div className="text-slate-400">—</div>
          )}
        </div>

        {/* Controller card */}
        <div className="p-4 rounded-lg bg-white shadow">
          <h3 className="font-medium mb-3">Controller</h3>
          {state ? (
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm">Current green</div>
                <div className="px-3 py-1 rounded bg-green-600 text-white font-medium">{state.current_green}</div>
              </div>

              <div>
                {approachOrder.map(a => {
                  const info = state.state?.[a] ?? { queue: 0, has_emergency: false }

                  return (
                    <div
                      key={a}
                      className={`p-3 mb-2 rounded ${state.current_green === a
                          ? 'bg-green-50 ring-1 ring-green-100'
                          : 'bg-slate-50'
                        }`}
                    >
                      {/* Header row */}
                      <div className="flex justify-between items-center mb-2">
                        <div className="font-medium flex items-center">
                          {a}
                          {/* 🚨 Add the EMG badge here */}
                          {info.has_emergency && (
                            <span className="ml-2 px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded animate-pulse">
                              EMG
                            </span>
                          )}
                        </div>

                        <div className="text-xs text-slate-500">
                          {info.has_emergency
                            ? `Emergency${info.exit ? ` → ${info.exit}` : ''}`
                            : `queue ${info.queue.toFixed(2)}`}
                        </div>
                      </div>

                      {/* Queue bar */}
                      <QueueBar
                        label={a}
                        value={info.queue}
                        max={queueMax}
                        isGreen={state.current_green === a}
                        emergency={info.has_emergency}
                      />
                    </div>
                  )
                })}

              </div>
            </div>
          ) : (
            <div className="text-slate-400">—</div>
          )}
        </div>
      </div>

      {/* Log */}
      <div className="p-4 rounded-lg bg-white shadow mb-6">
        <h3 className="font-medium mb-3">Log</h3>
        <div className="max-h-36 overflow-auto text-xs text-slate-700">
          {log.length === 0 ? (
            <div className="text-slate-400">No events yet</div>
          ) : (
            log.map((l, i) => (
              <div
                key={i}
                className={`p-1 border-b ${l.includes('❌')
                    ? 'bg-red-50 text-red-700'
                    : l.includes('✅')
                      ? 'bg-green-50 text-green-700'
                      : 'bg-white'
                  }`}
              >
                {l}
              </div>
            ))
          )}
        </div>

      </div>

      {/* toast */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-slate-900 text-white px-4 py-2 rounded shadow">
          {toast}
        </div>
      )}
    </div>
  )
}
