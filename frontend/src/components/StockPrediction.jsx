// frontend/src/components/StockPrediction.jsx
import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function StockPrediction({ onToast }){
  const [symbol, setSymbol] = useState('RELIANCE.NS')
  const [buyPrice, setBuyPrice] = useState('0')
  const [quantity, setQuantity] = useState('1')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function onSubmit(e){
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try{
      const data = await api('/api/predict_stock', {
        method: 'POST',
        body: {
          symbol: symbol.trim(),
          buy_price: parseFloat(buyPrice || '0'),
          quantity: parseInt(quantity || '1', 10)
        }
      })
      setResult(data)
      onToast?.('Prediction ready')
    }catch(err){
      const msg = err?.message || 'Failed to get prediction'
      setError(msg)
      onToast?.(msg)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-title">Stock Prediction</div>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          <div>Symbol</div>
          <input value={symbol} onChange={e=>setSymbol(e.target.value)} placeholder="e.g. RELIANCE.NS" />
        </label>
        <label>
          <div>Buy Price (₹)</div>
          <input type="number" step="0.01" value={buyPrice} onChange={e=>setBuyPrice(e.target.value)} />
        </label>
        <label>
          <div>Quantity</div>
          <input type="number" min="1" value={quantity} onChange={e=>setQuantity(e.target.value)} />
        </label>
        <div style={{display:'flex', alignItems:'flex-end'}}>
          <button className="btn" type="submit" disabled={loading}>{loading ? 'Predicting...' : 'Predict'}</button>
        </div>
      </form>

      {error && (
        <div className="alert error" style={{marginTop:12}}>{error}</div>
      )}

      {result && (
        <div className="card" style={{marginTop:16}}>
          <div className="card-title">Result</div>
          {result.degraded && (
            <div className="alert warning" style={{marginBottom:12}}>
              Data provider temporarily unavailable or rate-limited. Showing sentiment-only insights.
            </div>
          )}
          <div className="grid grid-2">
            <div>
              <div className="small text-muted">Symbol</div>
              <div>{result.symbol}</div>
            </div>
            <div>
              <div className="small text-muted">Current Price</div>
              <div>{result.current_price != null ? `₹${result.current_price}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Predicted Price</div>
              <div>{result.predicted_price != null ? `₹${result.predicted_price}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Potential Profit</div>
              <div>{result.potential_profit != null ? `₹${result.potential_profit}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">RSI</div>
              <div>{result.rsi != null ? result.rsi : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Sentiment</div>
              <div>{result.sentiment != null ? result.sentiment : 'N/A'}</div>
            </div>
            <div style={{gridColumn:'1 / -1'}}>
              <div className="small text-muted">Recommendation</div>
              <div>{result.recommendation || 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Model R²</div>
              <div>{result.r2 != null ? result.r2 : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">MAE</div>
              <div>{result.mae != null ? result.mae : 'N/A'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
