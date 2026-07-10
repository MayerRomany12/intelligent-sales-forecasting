import React, { useState } from 'react'

function App() {
  const [date, setDate] = useState('2018-08-20')
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [sequence, setSequence] = useState(null)
  const [error, setError] = useState(null)

  // Load API URL from env variables (Vite uses VITE_ prefix)
  const apiUrl = import.meta.env.VITE_API_URL || (window.location.hostname.includes('vercel.app') ? 'https://intelligent-sales-forecasting.vercel.app' : 'http://localhost:8000')

  const handlePredict = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPrediction(null)
    setSequence(null)

    try {
      // 1. Fetch Single Prediction
      const resSingle = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      })
      if (!resSingle.ok) throw new Error('Failed to fetch single date prediction')
      const dataSingle = await resSingle.json()
      setPrediction(dataSingle.forecasted_sales)

      // 2. Fetch Sequence Prediction
      const resSeq = await fetch(`${apiUrl}/predict/sequence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: date, days: parseInt(days) })
      })
      if (!resSeq.ok) throw new Error('Failed to fetch sequence prediction')
      const dataSeq = await resSeq.json()
      setSequence(dataSeq.predictions)

    } catch (err) {
      console.error(err)
      setError(err.message || 'An error occurred while communicating with the API server.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">Olist Sales Forecasting (React Client)</h1>
        <p className="subtitle">AI-Powered Sales Forecasting Platform running on FastAPI Backend</p>
      </header>

      <div className="content-grid">
        <div className="card control-card">
          <h2>Predictive Options</h2>
          <form onSubmit={handlePredict}>
            <div className="form-group">
              <label>Target Date:</label>
              <input 
                type="date" 
                value={date} 
                min="2016-09-04"
                max="2020-12-31"
                onChange={(e) => setDate(e.target.value)} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Forecast Horizon (Days):</label>
              <select value={days} onChange={(e) => setDays(e.target.value)}>
                {[3, 5, 7, 10, 14].map(d => (
                  <option key={d} value={d}>{d} Days</option>
                ))}
              </select>
            </div>

            <button type="submit" disabled={loading} className="btn-predict">
              {loading ? 'Calculating Forecast...' : 'Predict Sales'}
            </button>
          </form>

          {error && <div className="error-box">{error}</div>}
        </div>

        <div className="results-container">
          {prediction !== null && (
            <div className="glow-card">
              <div className="glow-title">Forecasted Sales</div>
              <div className="glow-value">${prediction.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
              <div className="glow-date">Target Date: {date}</div>
            </div>
          )}

          {sequence && (
            <div className="card table-card">
              <h2>{days}-Day Future Forecast Details</h2>
              <div className="table-responsive">
                <table className="forecast-table">
                  <thead>
                    <tr>
                      <th>Forecasted Date</th>
                      <th>Expected Sales ($)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sequence.map((pred, i) => (
                      <tr key={i}>
                        <td>{pred.date}</td>
                        <td className="sales-cell">${pred.forecasted_sales.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!prediction && !loading && !error && (
            <div className="placeholder-card">
              <p>Select a date and click "Predict Sales" to run the machine learning model.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
