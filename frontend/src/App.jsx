import { useEffect, useState } from 'react'
import './App.css'

const initialForm = {
  current_location: 'Chicago',
  pickup_location: 'Detroit',
  dropoff_location: 'Cleveland',
  current_cycle_used_hours: '20',
}

function App() {
  const [health, setHealth] = useState(null)
  const [form, setForm] = useState(initialForm)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [validationMessage, setValidationMessage] = useState('')

  useEffect(() => {
    fetch('/api/health/')
      .then((response) => response.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: 'error', message: 'Backend unavailable' }))
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setValidationMessage('')

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
      const response = await fetch('/api/trip-plan/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...trimmedForm,
          current_cycle_used_hours: cycleValue,
        }),
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(Object.values(data)[0]?.[0] || 'Unable to create trip plan')
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
        <p className="eyebrow">Full-stack assessment</p>
        <h1>Trip planning and ELD log generation</h1>
        <p className="hero-copy">
          Enter your trip details and the backend will return a route summary, rest recommendations,
          and daily ELD log entries.
        </p>

        <div className="status-panel">
          <h2>Backend status</h2>
          <p>{health ? health.message : 'Checking connection...'}</p>
          {health && <code>{health.status}</code>}
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

        {!plan && !loading && !error && !validationMessage && (
          <p className="empty-state">Submit trip details to generate a planning summary and ELD logs.</p>
        )}

        {plan && (
          <section className="plan-results">
            <div className="summary-grid">
              <article>
                <h2>Trip summary</h2>
                <p>Total distance: {plan.total_distance_miles} miles</p>
                <p>Drive hours: {plan.total_drive_hours}</p>
                <p>On-duty hours: {plan.total_on_duty_hours}</p>
                <p>Remaining cycle: {plan.remaining_cycle_hours} hrs</p>
                <p>Cycle status: {plan.cycle_status}</p>
              </article>
              <article>
                <h2>Rest recommendations</h2>
                {plan.required_rest_breaks.length > 0 ? (
                  plan.required_rest_breaks.map((item, index) => (
                    <p key={`${item.label}-${index}`}>{item.label}: {item.reason}</p>
                  ))
                ) : (
                  <p>No additional rest breaks required.</p>
                )}
              </article>
            </div>

            <div className="route-section">
              <h2>Route overview</h2>
              <div className="route-list">
                {plan.route_summary.map((step) => (
                  <div key={`${step.step}-${step.location}`} className="route-pill">
                    <strong>{step.type}</strong>
                    <span>{step.location}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="log-list">
              <h2>ELD daily logs</h2>
              {plan.eld_logs.map((entry) => (
                <article key={entry.day} className="log-card">
                  <h3>Day {entry.day}</h3>
                  <p>Driving: {entry.driving_hours} hrs</p>
                  <p>On-duty: {entry.on_duty_hours} hrs</p>
                  <p>Off-duty: {entry.off_duty_hours} hrs</p>
                  <p>Status: {entry.status}</p>
                  <p>Remarks: {entry.remarks}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
