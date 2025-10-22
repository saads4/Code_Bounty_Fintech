// frontend/src/pages/StockMind.jsx
import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function StockMind({ onToast }){
  const [ticker, setTicker] = useState('RELIANCE.NS')
  const [buyPrice, setBuyPrice] = useState('0')
  const [qty, setQty] = useState('1')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  async function onSubmit(e){
    e.preventDefault()
    setLoading(true)
    setResult(null)
    try{
      const data = await api('/api/stockmind/recommend', {
        method:'POST',
        body: { ticker, buy_price: parseFloat(buyPrice || '0'), quantity: parseInt(qty || '1', 10) }
      })
      setResult(data)
      onToast && onToast('StockMind recommendation ready')
    }catch(err){
      onToast && onToast(err.message || 'Failed to get recommendation')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <div className="card-title">StockMind — Intelligent Stock Insights</div>
        <form onSubmit={onSubmit} className="form-grid">
          <label>
            <div>Ticker</div>
            <input value={ticker} onChange={e=>setTicker(e.target.value)} placeholder="e.g. RELIANCE.NS" />
          </label>
          <label>
            <div>Buy Price (₹)</div>
            <input type="number" step="0.01" value={buyPrice} onChange={e=>setBuyPrice(e.target.value)} />
          </label>
          <label>
            <div>Quantity</div>
            <input type="number" min="1" value={qty} onChange={e=>setQty(e.target.value)} />
          </label>
          <div style={{display:'flex', alignItems:'flex-end'}}>
            <button className="btn" type="submit" disabled={loading}>{loading? 'Analyzing...' : 'Analyze'}</button>
          </div>
        </form>
      </div>

      {result && (
        <div className="card" style={{marginTop:16}}>
          <div className="card-title">Recommendation</div>
          {result.degraded && (
            <div className="alert warning" style={{marginBottom:12}}>
              Data provider rate-limited or unavailable. Showing sentiment-only insights.
            </div>
          )}
          <div className="grid grid-2">
            <div>
              <div className="small text-muted">Ticker</div>
              <div>{result.ticker}</div>
            </div>
            <div>
              <div className="small text-muted">Current Price</div>
              <div>{result.current_price != null ? `₹${result.current_price}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Predicted (raw)</div>
              <div>{result.predicted_price != null ? `₹${result.predicted_price}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Predicted (sentiment-adjusted)</div>
              <div>{result.adjusted_predicted_price != null ? `₹${result.adjusted_predicted_price}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Sentiment</div>
              <div>{result.sentiment != null ? result.sentiment : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">RSI</div>
              <div>{result.rsi != null ? result.rsi : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Advice</div>
              <div>{result.advice}</div>
            </div>
            <div>
              <div className="small text-muted">Potential P/L</div>
              <div>{result.potential_profit_loss != null ? `₹${result.potential_profit_loss}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Model R²</div>
              <div>{result.metrics?.r2 != null ? result.metrics.r2 : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">MAE</div>
              <div>{result.metrics?.mae != null ? result.metrics.mae : 'N/A'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
