import React, { useState, useMemo } from 'react'
import { getMondayBasedDayIndex } from '../utils/dateUtils'

export default function WeekdayDonutChart({ forecastData }) {
  const [hoveredSegment, setHoveredSegment] = useState(null)

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const colors = [
    '#00f2fe', // Monday - Cyan
    '#3b82f6', // Tuesday - Blue
    '#8b5cf6', // Wednesday - Purple
    '#ec4899', // Thursday - Pink
    '#f59e0b', // Friday - Amber
    '#10b981', // Saturday - Green
    '#ef4444'  // Sunday - Red
  ]

  // Group and compute shares
  const donutData = useMemo(() => {
    if (!forecastData || forecastData.length === 0) return []

    const stats = Array.from({ length: 7 }, (_, i) => ({
      dayIndex: i,
      dayName: dayNames[i],
      total: 0
    }))

    forecastData.forEach(item => {
      const idx = getMondayBasedDayIndex(item.date)
      if (idx !== null && idx >= 0 && idx < 7) {
        stats[idx].total += item.sales
      }
    })

    const totalSalesSum = stats.reduce((acc, curr) => acc + curr.total, 0)

    const radius = 40
    const circumference = 2 * Math.PI * radius

    // Filter out days with zero sales to avoid drawing empty slivers, but calculate percentage based on total
    let cumulativePercent = 0

    return stats.map((item, idx) => {
      const percent = totalSalesSum > 0 ? (item.total / totalSalesSum) * 100 : 0
      const strokeLength = (percent / 100) * circumference
      // Shift stroke offset backward clockwise
      const strokeOffset = circumference - (cumulativePercent / 100) * circumference
      cumulativePercent += percent

      return {
        ...item,
        percent,
        strokeLength,
        strokeOffset,
        color: colors[idx],
        circumference,
        radius
      }
    })
  }, [forecastData])

  const totalSum = useMemo(() => {
    return donutData.reduce((acc, curr) => acc + curr.total, 0)
  }, [donutData])

  if (donutData.length === 0 || totalSum === 0) {
    return (
      <div className="placeholder-card" style={{ minHeight: '200px' }}>
        <p>No forecast data available for distribution.</p>
      </div>
    )
  }

  // Segment to display in the middle hole (either hovered or the highest segment)
  const displaySegment = hoveredSegment || [...donutData].sort((a, b) => b.percent - a.percent)[0]

  return (
    <div className="chart-container-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: '200px', height: '200px' }}>
        <svg viewBox="0 0 120 120" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
          {/* Base circle background hole */}
          <circle
            cx="60"
            cy="60"
            r="40"
            fill="none"
            stroke="rgba(255, 255, 255, 0.02)"
            strokeWidth="10"
          />

          {/* Draw segments */}
          {donutData.map((seg, idx) => {
            if (seg.percent === 0) return null
            return (
              <circle
                key={idx}
                cx="60"
                cy="60"
                r="40"
                fill="none"
                stroke={seg.color}
                strokeWidth={hoveredSegment?.dayIndex === seg.dayIndex ? 12 : 10}
                strokeDasharray={`${seg.strokeLength} ${seg.circumference}`}
                strokeDashoffset={seg.strokeOffset}
                strokeLinecap="round"
                style={{
                  transition: 'stroke-width 0.3s ease, filter 0.3s ease',
                  cursor: 'pointer',
                  filter: hoveredSegment?.dayIndex === seg.dayIndex ? `drop-shadow(0 0 6px ${seg.color})` : 'none'
                }}
                onMouseEnter={() => setHoveredSegment(seg)}
                onMouseLeave={() => setHoveredSegment(null)}
              />
            )
          })}
        </svg>

        {/* Center Text inside the Donut Hole */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none',
          textAlign: 'center'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {displaySegment.dayName}
          </span>
          <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: displaySegment.color, margin: '2px 0' }}>
            {displaySegment.percent.toFixed(1)}%
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            ${Math.round(displaySegment.total).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Legend Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '0.5rem',
        marginTop: '1.25rem',
        width: '100%',
        borderTop: '1px solid rgba(255, 255, 255, 0.03)',
        paddingTop: '1rem'
      }}>
        {donutData.map((seg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.7rem',
              color: hoveredSegment?.dayIndex === seg.dayIndex ? '#ffffff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: hoveredSegment?.dayIndex === seg.dayIndex ? '600' : 'normal',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={() => setHoveredSegment(seg)}
            onMouseLeave={() => setHoveredSegment(null)}
          >
            <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', backgroundColor: seg.color }}></span>
            <span>{seg.dayName.substring(0, 3)} ({seg.percent.toFixed(0)}%)</span>
          </div>
        ))}
      </div>
    </div>
  )
}
