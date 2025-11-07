const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'


export async function startSim(cfg = { duration_s: 60, rps: 5 }){
const res = await fetch(`${BASE}/v1/sim/start`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(cfg) })
return res.json()
}


export async function getState(){
const res = await fetch(`${BASE}/v1/control/state`)
return res.json()
}


export async function getMetrics(){
const res = await fetch(`${BASE}/v1/metrics`)
return res.json()
}


export async function ingestPing(ping, token){
const res = await fetch(`${BASE}/v1/ingest`, {
method: 'POST',
headers: {
'Content-Type':'application/json',
'Authorization': `Bearer ${token||'DEMO_TOKEN_123'}`
},
body: JSON.stringify(ping)
})
return res.json()
}