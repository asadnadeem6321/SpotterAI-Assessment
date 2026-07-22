import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetch('/api/health/')
      .then((response) => response.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: 'error', message: 'Backend unavailable' }))
  }, [])

  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">Full-stack assessment</p>
        <h1>Trip planning and ELD log generation</h1>
        <p className="hero-copy">
          This project will combine a Django REST backend with a React frontend to calculate trip routes,
          rest requirements, and daily log sheets for commercial drivers.
        </p>
        <div className="status-panel">
          <h2>Backend status</h2>
          <p>{health ? health.message : 'Checking connection...'}</p>
          {health && <code>{health.status}</code>}
        </div>
      </section>
    </main>
  )
}

export default App
