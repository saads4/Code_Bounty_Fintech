// frontend/src/pages/Advisor.jsx
import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'

export default function Advisor({ onToast }){
  const [symbols, setSymbols] = useState([])
  const [symbol, setSymbol] = useState('')
  const [buyPrice, setBuyPrice] = useState('0')
  const [quantity, setQuantity] = useState('1')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(()=>{
    (async ()=>{
      try{
        const list = await api('/api/advisor/symbols')
        setSymbols(list)
        if(list.length) setSymbol(list[0])
      }catch(e){ onToast?.(e.message); setError(e.message) }
    })()
  },[])

  async function onSubmit(e){
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try{
      const data = await api('/api/advisor/recommend', {
        method: 'POST',
        body: {
          symbol: symbol,
          buy_price: parseFloat(buyPrice || '0'),
          quantity: parseInt(quantity || '1', 10)
        }
      })
      setResult(data)
      onToast?.('Advisor recommendation ready')
    }catch(err){
      const msg = err?.message || 'Failed to get recommendation'
      setError(msg)
      onToast?.(msg)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-title">Stock Advisor</div>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          <div>Symbol</div>
          <select value={symbol} onChange={e=>setSymbol(e.target.value)}>
            {symbols.map(s => (<option key={s} value={s}>{s}</option>))}
          </select>
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
          <button className="btn" type="submit" disabled={loading || !symbol}>{loading ? 'Analyzing...' : 'Get Recommendation'}</button>
        </div>
      </form>

      {error && (
        <div className="alert error" style={{marginTop:12}}>{error}</div>
      )}

      {result && (
        <div className="card" style={{marginTop:16}}>
          <div className="card-title">Result</div>
          <div className="grid grid-2">
            <div>
              <div className="small text-muted">Symbol</div>
              <div>{result.symbol}</div>
            </div>
            <div>
              <div className="small text-muted">Latest Close</div>
              <div>{result.latest_close != null ? `₹${result.latest_close}` : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Probability Up</div>
              <div>{result.prob_up != null ? result.prob_up : 'N/A'}</div>
            </div>
            <div>
              <div className="small text-muted">Unrealized P/L</div>
              <div>{result.profit_loss != null ? `₹${result.profit_loss}` : 'N/A'}</div>
            </div>
            <div style={{gridColumn:'1 / -1'}}>
              <div className="small text-muted">Decision</div>
              <div>{result.decision || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
