import React, { useMemo } from 'react'
import { getMondayBasedDayIndex } from '../utils/dateUtils'

export default function AIInsightsPanel({ forecastData, horizon }) {
  const calculations = useMemo(() => {
    if (!forecastData || forecastData.length === 0) return null

    // 1. Peak Sales Day
    const sales = forecastData.map(s => s.sales)
    const maxVal = Math.max(...sales)
    const peakItem = forecastData.find(s => s.sales === maxVal)

    // 2. Weekend vs Weekday Calculation
    let weekdayTotal = 0, weekdayCount = 0
    let weekendTotal = 0, weekendCount = 0
    forecastData.forEach(item => {
      const idx = getMondayBasedDayIndex(item.date)
      if (idx !== null) {
        if (idx === 5 || idx === 6) {
          weekendTotal += item.sales
          weekendCount += 1
        } else {
          weekdayTotal += item.sales
          weekdayCount += 1
        }
      }
    })
    const weekdayAvg = weekdayCount > 0 ? weekdayTotal / weekdayCount : 0
    const weekendAvg = weekendCount > 0 ? weekendTotal / weekendCount : 0
    const weekendDiff = weekdayAvg > 0 ? ((weekendAvg - weekdayAvg) / weekdayAvg) * 100 : null

    // 3. Growth Momentum
    const firstVal = sales[0]
    const lastVal = sales[sales.length - 1]
    const growthPercent = firstVal > 0 ? ((lastVal - firstVal) / firstVal) * 100 : 0

    // 4. Strongest Weekday
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    const dowTotal = Array(7).fill(0)
    const dowCount = Array(7).fill(0)
    forecastData.forEach(item => {
      const idx = getMondayBasedDayIndex(item.date)
      if (idx !== null) {
        dowTotal[idx] += item.sales
        dowCount[idx] += 1
      }
    })
    let bestDayIdx = -1
    let bestDayAvg = -1
    for (let i = 0; i < 7; i++) {
      if (dowCount[i] > 0) {
        const avg = dowTotal[i] / dowCount[i]
        if (avg > bestDayAvg) {
          bestDayAvg = avg
          bestDayIdx = i
        }
      }
    }

    return { peakItem, weekendDiff, growthPercent, bestDayIdx, bestDayAvg, dayNames, sales }
  }, [forecastData])

  const insights = useMemo(() => {
    if (!calculations) return null
    const { peakItem, weekendDiff, growthPercent, bestDayIdx, bestDayAvg, dayNames, sales } = calculations
    const items = []

    // Peak Day
    if (peakItem) {
      const avgSales = sales.reduce((a,b)=>a+b,0)/sales.length
      const diffPct = avgSales > 0 ? ((peakItem.sales / avgSales - 1) * 100) : 0
      items.push({
        id: 'peak',
        icon: '🚀',
        title: 'Peak Sales Day',
        desc: `Sales are expected to peak on ${peakItem.date} reaching $${Math.round(peakItem.sales).toLocaleString()}, which is ${Math.round(diffPct)}% above the horizon average.`
      })
    }

    // Weekend vs Weekday
    if (weekendDiff !== null) {
      let descText = ''
      if (Math.abs(weekendDiff) < 0.1) {
        descText = 'Weekend and weekday sales are projected to remain nearly equal, showing steady retail activity throughout the week.'
      } else if (weekendDiff > 0) {
        descText = `Weekend sales are forecasted to be ${weekendDiff.toFixed(1)}% higher than weekdays, indicating a strong surge in leisure shopping during the weekend.`
      } else {
        descText = `Weekend sales are forecasted to be ${Math.abs(weekendDiff).toFixed(1)}% lower than weekdays, suggesting a weekday-dominated purchase cycle driven by corporate or business purchases.`
      }
      items.push({
        id: 'weekend',
        icon: '📅',
        title: 'Weekly Cycle Analysis',
        desc: descText
      })
    }

    // Growth Momentum
    let growthDesc = ''
    if (growthPercent > 10) {
      growthDesc = `A strong upward momentum (+${growthPercent.toFixed(1)}%) is projected over the next ${horizon} days, indicating high demand and recommending stockpile preparedness.`
    } else if (growthPercent < -10) {
      growthDesc = `Sales are expected to cool down (-${Math.abs(growthPercent).toFixed(1)}%) over this period. This indicates post-peak normalization, useful for logistics adjustments.`
    } else {
      growthDesc = `Steady day-to-day consistency (growth of ${growthPercent.toFixed(1)}%) is forecasted, suggesting stable demand patterns without severe spikes.`
    }
    items.push({
      id: 'growth',
      icon: '📈',
      title: 'Growth Momentum',
      desc: growthDesc
    })

    // Seasonality
    if (bestDayIdx !== -1) {
      items.push({
        id: 'seasonality',
        icon: '⭐',
        title: 'Strongest Day Seasonality',
        desc: `${dayNames[bestDayIdx]} is predicted to be the strongest shopping day in the week, averaging $${Math.round(bestDayAvg).toLocaleString()} per day.`
      })
    }

    return items
  }, [calculations, horizon])

  const recommendations = useMemo(() => {
    if (!calculations) return null
    const { peakItem, weekendDiff, growthPercent, bestDayIdx, dayNames } = calculations
    const items = []

    // Recommendation 1: Inventory Buffer
    if (peakItem) {
      items.push({
        id: 'rec_inventory',
        icon: '📦',
        title: 'Inventory Safety Buffer',
        desc: `Raise warehouse safety stock by 25% starting 3 days before ${peakItem.date} to prevent stockouts and shipping backlogs during the predicted sales spike.`
      })
    }

    // Recommendation 2: Marketing Promotion
    if (weekendDiff !== null && weekendDiff < -5) {
      items.push({
        id: 'rec_marketing',
        icon: '📣',
        title: 'Weekend Promotion Stimulus',
        desc: `Weekend revenue lags by ${Math.abs(weekendDiff).toFixed(1)}%. Launch a "Weekend Free Shipping" coupon or flash email campaign on Fridays to capture retail buyers.`
      })
    } else {
      items.push({
        id: 'rec_marketing',
        icon: '📣',
        title: 'Fulfillment & Loyalty Booster',
        desc: `Weekend performance is strong. Channel promotional budgets into weekday loyalty points modifiers to capture B2B shoppers.`
      })
    }

    // Recommendation 3: Staffing Allocation
    if (bestDayIdx !== -1) {
      const bestDay = dayNames[bestDayIdx]
      items.push({
        id: 'rec_staff',
        icon: '👥',
        title: 'Fulfillment Shift Allocation',
        desc: `Allocate 15% more warehouse packing staff and support agents on ${bestDay}s to handle the weekly peak order volumes.`
      })
    }

    // Recommendation 4: Pricing Strategy
    if (growthPercent > 10) {
      items.push({
        id: 'rec_price',
        icon: '💰',
        title: 'Price Optimization Margin',
        desc: `Demand is surging (+${growthPercent.toFixed(1)}%). Consider raising pricing benchmarks slightly and pausing clearance discounts to maximize margins.`
      })
    } else if (growthPercent < -10) {
      items.push({
        id: 'rec_price',
        icon: '💰',
        title: 'Volume Stimulation Discounts',
        desc: `Sales are expected to contract (-${Math.abs(growthPercent).toFixed(1)}%). Launch bundle discounts or a 15% flash sale to stimulate order volume.`
      })
    } else {
      items.push({
        id: 'rec_price',
        icon: '💰',
        title: 'Bundle Pricing Policy',
        desc: `Demand is stable. Maintain standard pricing baselines. Implement value-added product bundling to increase Average Order Value (AOV).`
      })
    }

    return items
  }, [calculations])

  if (!insights || !recommendations) return null

  return (
    <div className="card ai-insights-card fade-in" style={{ animationDelay: '0.4s' }}>
      <div className="insights-panel-split" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2.5rem' }}>
        
        {/* Left: AI Insights */}
        <div>
          <h2>🤖 Predictive AI Insights</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '1.5rem' }}>
            {insights.map(item => (
              <div key={item.id} className="insight-item">
                <span className="insight-icon">{item.icon}</span>
                <div className="insight-content">
                  <h4>{item.title}</h4>
                  <p>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: AI Recommendations */}
        <div>
          <h2>💡 Strategic Recommendations</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '1.5rem' }}>
            {recommendations.map(item => (
              <div key={item.id} className="insight-item rec-item">
                <span className="insight-icon rec-icon">{item.icon}</span>
                <div className="insight-content">
                  <h4>{item.title}</h4>
                  <p>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
