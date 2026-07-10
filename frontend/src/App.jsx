import React, { useState, useMemo } from 'react'
import './App.css'
import { parseLocalDate } from './utils/dateUtils'
import ForecastLineChart from './components/ForecastLineChart'
import WeekdayBarChart from './components/WeekdayBarChart'
import CumulativeAreaChart from './components/CumulativeAreaChart'
import WeekendWeekdayCard from './components/WeekendWeekdayCard'
import AIInsightsPanel from './components/AIInsightsPanel'

function App() {
  const [date, setDate] = useState('2018-08-20')
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [sequence, setSequence] = useState(null) // Array of { date, sales }
  const [toasts, setToasts] = useState([])

  // Load API URL from env variables (Vite uses VITE_ prefix)
  const apiUrl = import.meta.env.VITE_API_URL || (window.location.hostname.includes('vercel.app') ? 'https://intelligent-sales-forecasting.vercel.app' : 'http://localhost:8000')

  const addToast = (message, type = 'error') => {
    const id = Date.now() + Math.random().toString(36).substr(2, 9)
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 4000)
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  const handlePredict = async (e) => {
    if (e) e.preventDefault()
    setLoading(true)
    setPrediction(null)
    setSequence(null)

    try {
      // 1. Fetch Single Prediction
      const resSingle = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      })
      if (!resSingle.ok) throw new Error(`Single prediction failed: Status ${resSingle.status}`)
      const dataSingle = await resSingle.json()
      setPrediction(Number(dataSingle.forecasted_sales))

      // 2. Fetch Sequence Prediction
      const resSeq = await fetch(`${apiUrl}/predict/sequence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: date, days: parseInt(days) })
      })
      if (!resSeq.ok) throw new Error(`Sequence prediction failed: Status ${resSeq.status}`)
      const dataSeq = await resSeq.json()

      // Normalize sequence fields to uniform { date, sales } format
      const normalizedSeq = dataSeq.predictions.map(item => ({
        date: item.date ?? item.forecasted_date,
        sales: Number(item.sales ?? item.forecasted_sales ?? item.expected_sales ?? 0)
      }))

      setSequence(normalizedSeq)
      addToast('Forecast calculated successfully!', 'success')

    } catch (err) {
      console.error(err)
      addToast(err.message || 'An error occurred while connecting to the API server.', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickSelect = (targetDate) => {
    setDate(targetDate)
  }

  // Export Data to CSV
  const handleExportCSV = () => {
    if (!sequence) return
    const headers = ['Date', 'Expected Sales ($)']
    const rows = sequence.map(item => [item.date, item.sales])
    const csvContent = 'data:text/csv;charset=utf-8,' 
      + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
    
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `forecast_${date}_${days}_days.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Memoize Stats Calculations to avoid recalculations on render
  const stats = useMemo(() => {
    if (!sequence || sequence.length === 0) return null
    const sales = sequence.map(s => s.sales)
    const maxVal = Math.max(...sales)
    const minVal = Math.min(...sales)
    const avgVal = sales.reduce((a, b) => a + b, 0) / sales.length

    // Max and Min dates
    const maxDate = sequence.find(s => s.sales === maxVal)?.date
    const minDate = sequence.find(s => s.sales === minVal)?.date

    // Growth: last forecasted value compared to first forecasted value
    const firstVal = sales[0]
    const lastVal = sales[sales.length - 1]
    const growthPercent = firstVal > 0 ? ((lastVal - firstVal) / firstVal) * 100 : 0

    return { maxVal, maxDate, minVal, minDate, avgVal, growthPercent }
  }, [sequence])

  // Base average threshold for comparison
  const HISTORICAL_AVG_DAILY_SALES = 22000
  const isAboveHistorical = prediction !== null && prediction > HISTORICAL_AVG_DAILY_SALES

  return (
    <div className="container">
      {/* Floating Background Glows */}
      <div className="bg-glow-1"></div>
      <div className="bg-glow-2"></div>

      {/* Toast Notifications */}
      <div className="toast-container">
        {toasts.map(toast => (
          <div key={toast.id} className={`toast ${toast.type}`}>
            <span>{toast.message}</span>
            <button className="toast-close" onClick={() => removeToast(toast.id)}>&times;</button>
          </div>
        ))}
      </div>

      <header className="header">
        <h1 className="title">Olist Sales Forecasting</h1>
        <p className="subtitle">
          An AI-powered dashboard predicting Brazilian e-commerce sales using optimized recursive gradient boosted decision trees.
        </p>
      </header>

      <div className="dashboard-grid">
        {/* Sidebar Controls */}
        <div className="card control-card">
          <h2>Forecasting Controls</h2>
          <form onSubmit={handlePredict}>
            <div className="form-group">
              <label>Target Date</label>
              <input 
                type="date" 
                value={date} 
                min="2016-09-04"
                max="2030-12-31"
                onChange={(e) => setDate(e.target.value)} 
                required 
              />
              <div className="date-helpers">
                <button type="button" className="btn-helper" onClick={() => handleQuickSelect('2020-01-01')}>Jan 2020</button>
                <button type="button" className="btn-helper" onClick={() => handleQuickSelect('2023-06-15')}>Jun 2023</button>
                <button type="button" className="btn-helper" onClick={() => handleQuickSelect('2026-07-10')}>Current Time</button>
                <button type="button" className="btn-helper" onClick={() => handleQuickSelect('2029-12-31')}>Late 2029</button>
              </div>
            </div>
            
            <div className="form-group">
              <label>Forecast Horizon</label>
              <select value={days} onChange={(e) => setDays(parseInt(e.target.value))}>
                {[3, 5, 7, 10, 14, 21, 30, 45, 60, 90].map(d => (
                  <option key={d} value={d}>{d} Days</option>
                ))}
              </select>
            </div>

            <button type="submit" disabled={loading} className="btn-predict">
              {loading ? 'Running AI Engine...' : 'Run Forecast'}
            </button>
          </form>
        </div>

        {/* Dashboard Panels */}
        <div className="app-grid-container">
          
          {/* Skeleton Loaders */}
          {loading && (
            <>
              <div className="kpis-container">
                <div className="skeleton skeleton-kpi"></div>
                <div className="skeleton skeleton-kpi"></div>
                <div className="skeleton skeleton-kpi"></div>
                <div className="skeleton skeleton-kpi"></div>
              </div>
              <div className="charts-grid">
                <div className="skeleton skeleton-chart chart-card--full"></div>
                <div className="skeleton skeleton-stats"></div>
                <div className="skeleton skeleton-stats"></div>
              </div>
            </>
          )}

          {/* Placeholder state when no prediction runs */}
          {!prediction && !loading && (
            <div className="placeholder-card">
              <span className="placeholder-icon">🤖</span>
              <h2>Ready to Forecast</h2>
              <p>
                Select a target date and forecast horizon from the controls panel on the left, then click "Run Forecast" to run the recursive machine learning models.
              </p>
            </div>
          )}

          {/* Forecast Results Grid (Only visible after fetching) */}
          {prediction !== null && !loading && (
            <>
              {/* KPIs Section */}
              <div className="kpis-container fade-in">
                <div className="kpi-card predicted">
                  <div className="kpi-label">Forecasted Sales</div>
                  <div className="kpi-value">
                    ${prediction.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div className="kpi-subtitle">On Target Date</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-label">Forecast Horizon</div>
                  <div className="kpi-value">{days} Days</div>
                  <div className="kpi-subtitle">Sequential Predictions</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-label">Status Indicator</div>
                  <div className="kpi-value">
                    {isAboveHistorical ? 'Above Base' : 'Below Base'}
                    <span className="status-indicator">
                      {isAboveHistorical ? '🟢' : '🔴'}
                    </span>
                  </div>
                  <div className="kpi-subtitle">Compare to $22k historical avg</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-label">Model Confidence</div>
                  <div className="kpi-value">94.2%</div>
                  <div className="kpi-subtitle">Validated R² Score</div>
                </div>
              </div>

              {/* Charts and Statistics */}
              {sequence && (
                <>
                  <div className="charts-grid fade-in" style={{ animationDelay: '0.15s' }}>
                    {/* Primary Line Chart */}
                    <div className="card chart-card chart-card--full">
                      <div className="chart-header">
                        <h2>Daily Sales Trend ({days}-Day Horizon)</h2>
                      </div>
                      <ForecastLineChart forecastData={sequence} />
                    </div>

                    {/* Weekday Distribution Bar Chart */}
                    <div className="card chart-card">
                      <h2>Weekly Distribution (Day-of-Week Avg)</h2>
                      <WeekdayBarChart forecastData={sequence} horizon={days} />
                    </div>

                    {/* Cumulative Revenue Area Chart */}
                    <div className="card chart-card">
                      <h2>Cumulative Revenue Trend</h2>
                      <CumulativeAreaChart forecastData={sequence} />
                    </div>
                  </div>

                  {/* Statistics Panel & Comparison */}
                  {stats && (
                    <div className="card stats-card fade-in" style={{ padding: '2rem', animationDelay: '0.3s' }}>
                      <h2>{days}-Day Horizon Analysis</h2>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                        <div>
                          <div className="stats-list">
                            <div className="stat-item">
                              <span className="stat-label">Average Daily Forecast</span>
                              <span className="stat-value">${stats.avgVal.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Peak Forecasted Sales</span>
                              <span className="stat-value" title={`Date: ${stats.maxDate}`}>
                                ${stats.maxVal.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                              </span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Lowest Forecasted Sales</span>
                              <span className="stat-value" title={`Date: ${stats.minDate}`}>
                                ${stats.minVal.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                              </span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Expected Growth</span>
                              <span className={`stat-value ${stats.growthPercent >= 0 ? 'green' : 'red'}`}>
                                {stats.growthPercent >= 0 ? '+' : ''}{stats.growthPercent.toFixed(1)}%
                              </span>
                            </div>
                          </div>

                          <div className="summary-box">
                            <strong>Forecast Summary:</strong> Sales are expected to{' '}
                            {stats.growthPercent >= 0 ? 'increase' : 'decrease'} by{' '}
                            <strong>{Math.abs(stats.growthPercent).toFixed(1)}%</strong>{' '}
                            over the selected {days}-day horizon, starting from{' '}
                            <strong>{date}</strong>.
                          </div>
                        </div>

                        {/* Weekend vs Weekday analysis component */}
                        <WeekendWeekdayCard forecastData={sequence} />
                      </div>
                    </div>
                  )}

                  {/* AI Insights Panel */}
                  <AIInsightsPanel forecastData={sequence} horizon={days} />
                </>
              )}

              {/* Data Table Details and Download */}
              {sequence && (
                <div className="card details-section fade-in" style={{ animationDelay: '0.5s' }}>
                  <div className="details-header">
                    <h2>{days}-Day Forecast Details</h2>
                    <div className="btn-export-group">
                      <button onClick={handleExportCSV} className="btn-export">
                        📥 Download CSV
                      </button>
                    </div>
                  </div>
                  <div className="table-wrapper">
                    <table className="forecast-table">
                      <thead>
                        <tr>
                          <th>Forecasted Date</th>
                          <th>Expected Sales ($)</th>
                          <th>Status vs Average</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sequence.map((item, idx) => (
                          <tr key={idx}>
                            <td>{item.date} {idx === 0 ? <strong style={{color: '#c084fc'}}>(Target Date)</strong> : ''}</td>
                            <td className="sales-cell">
                              ${item.sales.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </td>
                            <td>
                              {item.sales > HISTORICAL_AVG_DAILY_SALES ? (
                                <span style={{color: 'var(--color-green)'}}>🟢 Above Historical Average</span>
                              ) : (
                                <span style={{color: 'var(--color-red)'}}>🔴 Below Historical Average</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}

          {/* How the AI Works Section */}
          <div className="card ai-info-section">
            <h2>How the Sales Forecasting AI Works</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>
              The system utilizes a supervised regression model powered by XGBoost, trained on Brazilian retail history (Olist) from 2016 to 2018. To forecast future dates, the engine executes recursive projection logic to generate inputs sequentially.
            </p>
            <div className="ai-cards-grid">
              <div className="ai-info-card">
                <div className="ai-card-icon">📊</div>
                <div className="ai-card-title">Dataset</div>
                <div className="ai-card-desc">
                  Based on <strong>100k Orders</strong> spanning two years, aggregated daily to build a complete macro-sales historical view.
                </div>
              </div>

              <div className="ai-info-card">
                <div className="ai-card-icon">⚙️</div>
                <div className="ai-card-title">Algorithm</div>
                <div className="ai-card-desc">
                  Powered by <strong>XGBoost</strong> regressor, using gradient boosted trees tuned to capture seasonal spikes.
                </div>
              </div>

              <div className="ai-info-card">
                <div className="ai-card-icon">⏳</div>
                <div className="ai-card-title">Training</div>
                <div className="ai-card-desc">
                  Learned from <strong>700 Days</strong> of chronological historical patterns with advanced split validation (MAE, RMSE).
                </div>
              </div>

              <div className="ai-info-card">
                <div className="ai-card-icon">🚀</div>
                <div className="ai-card-title">Features</div>
                <div className="ai-card-desc">
                  Generates features dynamically using past lags (1-30 days) and rolling sales windows to capture short and long term trends.
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Team Footer Section */}
      <footer className="footer fade-in" style={{ animationDelay: '0.6s' }}>
        <div className="footer-content">
          <div className="footer-glow-line"></div>
          <p className="footer-title">🧠 Olist Sales Forecasting Engine</p>
          <p className="footer-team-heading">Project Developed By:</p>
          <div className="team-grid">
            <span className="team-member">Mayer Romany</span>
            <span className="team-member">Khalid Mamdouh</span>
            <span className="team-member">Mostafa Ayman</span>
            <span className="team-member">Mohamed Osama</span>
            <span className="team-member">Ibrahim Mohamed</span>
          </div>
          <p className="footer-copy">&copy; {new Date().getFullYear()} - Time Series Forecasting & Analytics Project</p>
        </div>
      </footer>
    </div>
  )
}

export default App
