import React, { useState } from 'react'

export default function ForecastLineChart({ forecastData }) {
  const [activeTooltip, setActiveTooltip] = useState(null)

  if (!forecastData || forecastData.length === 0) {
    return (
      <div className="placeholder-card" style={{ minHeight: '300px' }}>
        <p>No forecast data available.</p>
      </div>
    )
  }

  const svgWidth = 800
  const svgHeight = 320
  const paddingLeft = 70
  const paddingRight = 40
  const paddingTop = 40
  const paddingBottom = 50

  const chartWidth = svgWidth - paddingLeft - paddingRight
  const chartHeight = svgHeight - paddingTop - paddingBottom

  const salesList = forecastData.map(s => s.sales)
  const minSales = Math.min(...salesList)
  const maxSales = Math.max(...salesList)
  const salesRange = maxSales - minSales || 1

  const yMin = Math.max(0, minSales - salesRange * 0.15)
  const yMax = maxSales + salesRange * 0.15
  const ySpan = yMax - yMin

  // Map data points
  const points = forecastData.map((item, index) => {
    const x = paddingLeft + (forecastData.length > 1 ? (index / (forecastData.length - 1)) * chartWidth : chartWidth / 2)
    const y = paddingTop + chartHeight - ((item.sales - yMin) / ySpan) * chartHeight
    return { x, y, date: item.date, sales: item.sales, index }
  })

  // SVG paths
  const linePath = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  const areaPath = forecastData.length > 1 
    ? `${linePath} L ${points[points.length - 1].x} ${paddingTop + chartHeight} L ${points[0].x} ${paddingTop + chartHeight} Z`
    : ''

  // Grid lines count
  const gridLines = 5
  const yGridValues = Array.from({ length: gridLines }, (_, i) => yMin + (i / (gridLines - 1)) * ySpan)

  // X-axis label display logic to avoid cluttering
  const showXAxisLabelInterval = forecastData.length > 20 ? 6 : forecastData.length > 10 ? 3 : 1

  return (
    <div className="chart-container-inner" style={{ position: 'relative', width: '100%', flexGrow: 1 }}>
      <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="svg-chart" style={{ width: '100%', height: '300px', overflow: 'visible' }}>
        <defs>
          <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00f2fe" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#4facfe" stopOpacity="0.0" />
          </linearGradient>
          <linearGradient id="chart-line-gradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#00f2fe" />
            <stop offset="50%" stopColor="#4facfe" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {yGridValues.map((val, idx) => {
          const y = paddingTop + chartHeight - ((val - yMin) / ySpan) * chartHeight
          return (
            <g key={idx}>
              <line x1={paddingLeft} y1={y} x2={svgWidth - paddingRight} y2={y} className="chart-grid-line" />
              <text x={paddingLeft - 10} y={y + 4} className="chart-axis-text y-axis">
                ${Math.round(val).toLocaleString()}
              </text>
            </g>
          )
        })}

        {/* X axis line */}
        <line x1={paddingLeft} y1={paddingTop + chartHeight} x2={svgWidth - paddingRight} y2={paddingTop + chartHeight} className="chart-axis-line" />

        {/* Tracker Crosshair */}
        {activeTooltip && (
          <line
            x1={activeTooltip.x}
            y1={paddingTop}
            x2={activeTooltip.x}
            y2={paddingTop + chartHeight}
            stroke="rgba(0, 242, 254, 0.35)"
            strokeDasharray="4 4"
            strokeWidth="1.5"
            style={{ pointerEvents: 'none' }}
          />
        )}

        {/* Area & Line */}
        {forecastData.length > 1 && <path d={areaPath} className="chart-area" />}
        <path d={linePath} className="chart-line" />

        {/* X labels */}
        {points.map((p, idx) => {
          if (idx % showXAxisLabelInterval === 0 || idx === points.length - 1) {
            const formattedDate = p.date.substring(5) // MM-DD format
            return (
              <text key={idx} x={p.x} y={paddingTop + chartHeight + 20} className="chart-axis-text x-axis">
                {formattedDate}
              </text>
            )
          }
          return null
        })}

        {/* Interactive nodes */}
        {points.map((p, idx) => {
          const isDense = forecastData.length > 30;
          const rSize = idx === 0 ? (isDense ? 4.5 : 6) : (isDense ? 1.5 : 4);
          return (
            <circle
              key={idx}
              cx={p.x}
              cy={p.y}
              r={rSize}
              className={idx === 0 ? 'chart-prediction-point' : 'chart-node'}
              onMouseEnter={() => {
                setActiveTooltip({
                  x: p.x,
                  y: p.y - 10,
                  date: p.date,
                  sales: p.sales
                })
              }}
              onMouseLeave={() => setActiveTooltip(null)}
            />
          )
        })}
      </svg>

      {activeTooltip && (
        <div 
          className="chart-tooltip"
          style={{ 
            // Bound left between 5% and 85% to keep tooltip in viewport
            left: `${Math.max(5, Math.min(85, ((activeTooltip.x - paddingLeft) / chartWidth) * 100 + 4))}%`,
            top: `${((activeTooltip.y - paddingTop) / chartHeight) * 100 - 15}%` 
          }}
        >
          <span className="tooltip-date">{activeTooltip.date}</span>
          <span className="tooltip-sales">${activeTooltip.sales.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
        </div>
      )}
    </div>
  )
}
