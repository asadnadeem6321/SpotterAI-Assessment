import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'

const initialForm = {
  current_location: 'Chicago',
  pickup_location: 'Detroit',
  dropoff_location: 'Cleveland',
  current_cycle_used_hours: '20',
}

const presetRoutes = [
  {
    id: 'midwest',
    label: 'Midwest run',
    values: {
      current_location: 'Chicago',
      pickup_location: 'Detroit',
      dropoff_location: 'Cleveland',
      current_cycle_used_hours: '20',
    },
  },
  {
    id: 'mountain',
    label: 'Mountain haul',
    values: {
      current_location: 'Chicago',
      pickup_location: 'Denver',
      dropoff_location: 'Phoenix',
      current_cycle_used_hours: '8',
    },
  },
]

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

function App() {
  const [health, setHealth] = useState(null)
  const [form, setForm] = useState(initialForm)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [validationMessage, setValidationMessage] = useState('')

  const routeMap = plan?.route_map

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health/`)
        const data = await response.json()
        setHealth({ status: response.ok ? 'ok' : 'error', ...data })
      } catch {
        setHealth({ status: 'error', message: 'Backend unavailable' })
      }
    }

    checkHealth()
  }, [])

  const buildLogSegments = (entry) => {
    const drivingWidth = Math.max(0, Math.min(100, (entry.driving_hours / 24) * 100))
    const onDutyWidth = Math.max(0, Math.min(100, (entry.on_duty_hours / 24) * 100))
    const offDutyWidth = Math.max(0, 100 - onDutyWidth)

    return [
      { label: 'Driving', width: drivingWidth, className: 'segment-driving' },
      { label: 'On-duty', width: onDutyWidth - drivingWidth, className: 'segment-duty' },
      { label: 'Off-duty', width: offDutyWidth, className: 'segment-rest' },
    ].filter((segment) => segment.width > 0.2)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setValidationMessage('')
    setPlan(null)

    const trimmedForm = {
      ...form,
      current_location: form.current_location.trim(),
      pickup_location: form.pickup_location.trim(),
      dropoff_location: form.dropoff_location.trim(),
    }

    if (!trimmedForm.current_location || !trimmedForm.pickup_location || !trimmedForm.dropoff_location) {
      setValidationMessage('Please fill in all location fields before generating a plan.')
      setLoading(false)
      return
    }

    const cycleValue = Number(trimmedForm.current_cycle_used_hours)
    if (Number.isNaN(cycleValue) || cycleValue < 0 || cycleValue > 70) {
      setValidationMessage('Cycle hours must be a number between 0 and 70.')
      setLoading(false)
      return
    }

    setForm({ ...form, ...trimmedForm, current_cycle_used_hours: String(cycleValue) })

    try {
      const response = await fetch(`${API_BASE_URL}/trip-plan/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...trimmedForm,
          current_cycle_used_hours: cycleValue,
        }),
      })

      const contentType = response.headers.get('content-type') || ''
      let data
      if (contentType.includes('application/json')) {
        data = await response.json()
      } else {
        data = await response.text()
      }

      if (!response.ok) {
        const message = typeof data === 'string'
          ? data
          : Object.values(data)[0]?.[0] || 'Unable to create trip plan'
        throw new Error(message)
      }

      setPlan(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div className="hero-top">
          <div>
            <p className="eyebrow">Fleet operations planner</p>
            <h1>Design safer trips and ELD-ready daily logs in minutes.</h1>
            <p className="hero-copy">
              Submit a route, and the backend will return a practical plan with rest recommendations,
              cycle insights, map guidance, and step-by-step route instructions.
            </p>
          </div>
          <div className={`status-pill ${health?.status === 'ok' ? 'online' : 'offline'}`}>
            <span className="status-dot" />
            {health?.status === 'ok' ? 'Backend connected' : 'Backend offline'}
          </div>
        </div>

        <div className="hero-grid">
          <div className="panel-card form-panel">
            <div className="panel-title-row">
              <h2>Trip inputs</h2>
              <span className="subtle-pill">Live API</span>
            </div>

            <div className="preset-row">
              {presetRoutes.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  className="preset-btn"
                  onClick={() => setForm({ ...form, ...preset.values })}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            <form className="trip-form" onSubmit={handleSubmit}>
              <label>
                Current location
                <input
                  value={form.current_location}
                  onChange={(event) => setForm({ ...form, current_location: event.target.value })}
                />
              </label>
              <label>
                Pickup location
                <input
                  value={form.pickup_location}
                  onChange={(event) => setForm({ ...form, pickup_location: event.target.value })}
                />
              </label>
              <label>
                Dropoff location
                <input
                  value={form.dropoff_location}
                  onChange={(event) => setForm({ ...form, dropoff_location: event.target.value })}
                />
              </label>
              <label>
                Current cycle used (hrs)
                <input
                  type="number"
                  min="0"
                  max="70"
                  value={form.current_cycle_used_hours}
                  onChange={(event) => setForm({ ...form, current_cycle_used_hours: event.target.value })}
                />
              </label>
              <button type="submit" disabled={loading}>
                {loading ? 'Planning...' : 'Generate plan'}
              </button>
            </form>

            {validationMessage && <p className="error-text">{validationMessage}</p>}
            {error && <p className="error-text">{error}</p>}
          </div>

          <div className="panel-card insight-panel">
            <h2>What the planner checks</h2>
            <ul>
              <li>Cycle hour limits and remaining availability</li>
              <li>Daily drive/on-duty thresholds</li>
              <li>Rest-break recommendations and fueling stops</li>
              <li>ELD-style daily logs with route guidance</li>
              <li>Map coordinates and route path visuals</li>
            </ul>
            <div className="status-box">
              <h3>Backend status</h3>
              <p>{health ? health.message : 'Checking connection...'}</p>
              {health && <code>{health.status}</code>}
            </div>
          </div>
        </div>

        {!plan && !loading && !error && !validationMessage && (
          <div className="empty-state-card">
            <h2>Start with a route</h2>
            <p>Enter a trip and generate a polished planning summary that feels ready for submission.</p>
          </div>
        )}

        {loading && !plan && (
          <div className="empty-state-card loading-card">
            <h2>Building your plan</h2>
            <p>Connecting to the backend and generating the trip summary.</p>
          </div>
        )}

        {plan && (
          <section className="plan-results">
            <div className="summary-grid">
              <article className="result-card highlight-card">
                <div className="panel-title-row">
                  <h2>Trip snapshot</h2>
                  <span className={`status-chip ${plan.cycle_status}`}>{plan.cycle_status}</span>
                </div>
                <div className="metrics-grid">
                  <div className="metric-pill">
                    <span>Distance</span>
                    <strong>{plan.total_distance_miles} mi</strong>
                  </div>
                  <div className="metric-pill">
                    <span>Drive</span>
                    <strong>{plan.total_drive_hours} hrs</strong>
                  </div>
                  <div className="metric-pill">
                    <span>On-duty</span>
                    <strong>{plan.total_on_duty_hours} hrs</strong>
                  </div>
                  <div className="metric-pill">
                    <span>Remaining cycle</span>
                    <strong>{plan.remaining_cycle_hours} hrs</strong>
                  </div>
                  <div className="metric-pill">
                    <span>Cycle window</span>
                    <strong>8 days</strong>
                  </div>
                </div>
                {plan.warnings.length > 0 && (
                  <div className="warning-list">
                    {plan.warnings.map((warning, index) => (
                      <p key={`${warning}-${index}`}>⚠ {warning}</p>
                    ))}
                  </div>
                )}
              </article>

              <article className="result-card">
                <h2>Rest recommendations</h2>
                {plan.required_rest_breaks.length > 0 ? (
                  <div className="stack-list">
                    {plan.required_rest_breaks.map((item, index) => (
                      <div key={`${item.label}-${index}`} className="list-item">
                        <strong>{item.label}</strong>
                        <p>{item.reason}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted-text">No additional rest breaks required.</p>
                )}
              </article>
            </div>

            <div className="results-grid">
              <article className="result-card">
                <h2>Route map</h2>
                {routeMap ? (
                  <div className="map-card">
                    <MapContainer
                      center={[routeMap.center.lat, routeMap.center.lng]}
                      zoom={5}
                      scrollWheelZoom={false}
                      className="trip-map"
                    >
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      />
                      <Polyline
                        positions={routeMap.path.map((point) => [point.lat, point.lng])}
                        pathOptions={{ color: '#2563eb', weight: 4 }}
                      />
                      {routeMap.points.map((point) => (
                        <CircleMarker
                          key={`${point.label}-${point.location}`}
                          center={[point.lat, point.lng]}
                          radius={9}
                          pathOptions={{ color: '#1d4ed8', fillColor: '#60a5fa', fillOpacity: 0.95 }}
                        >
                          <Popup>
                            <strong>{point.label}</strong>
                            <br />
                            {point.location}
                          </Popup>
                        </CircleMarker>
                      ))}
                    </MapContainer>
                    <div className="map-legend">
                      {routeMap.points.map((point) => (
                        <div key={`${point.label}-${point.location}`} className="legend-item">
                          <span className="legend-dot" />
                          <div>
                            <strong>{point.label}</strong>
                            <p>{point.location}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </article>

              <article className="result-card">
                <h2>Route instructions</h2>
                <div className="route-visual">
                  {plan.route_summary.map((step, index) => (
                    <div key={`${step.step}-${step.location}`} className="route-node">
                      <div className="route-node-marker">{index + 1}</div>
                      <div className="route-node-body">
                        <strong>{step.type}</strong>
                        <h3>{step.location}</h3>
                        <p>{step.instruction}</p>
                        <span>{step.distance_miles} mi • {step.estimated_duration_hours} hrs</span>
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="result-card">
                <h2>ELD daily logs</h2>
                <div className="log-list">
                  {plan.eld_logs.map((entry) => (
                    <article key={entry.day} className="log-card">
                      <div className="panel-title-row">
                        <h3>Day {entry.day}</h3>
                        <span className="subtle-pill">{entry.status}</span>
                      </div>
                      <div className="log-sheet">
                        <div className="log-scale">
                          <span>0</span>
                          <span>6</span>
                          <span>12</span>
                          <span>18</span>
                          <span>24</span>
                        </div>
                        <div className="log-bar">
                          {buildLogSegments(entry).map((segment) => (
                            <div
                              key={segment.label}
                              className={`log-segment ${segment.className}`}
                              style={{ width: `${segment.width}%` }}
                            >
                              <span>{segment.label}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="log-metrics">
                        <p>Driving: {entry.driving_hours} hrs</p>
                        <p>On-duty: {entry.on_duty_hours} hrs</p>
                        <p>Off-duty: {entry.off_duty_hours} hrs</p>
                        <p>Cycle window: {entry.cycle_window_days} days</p>
                      </div>
                      <p>Remarks: {entry.remarks}</p>
                    </article>
                  ))}
                </div>
              </article>
            </div>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
