import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import StockPrediction from '../components/StockPrediction.jsx'

export default function Dashboard({ onToast }){
  const [kpis, setKpis] = useState({})
  const [series, setSeries] = useState([])

  useEffect(()=>{
    (async ()=>{
      try{
        setKpis(await api('/api/dashboard/kpis'))
        setSeries(Array.from({length:60}).map((_,i)=>({x:i, val: Math.sin(i/8)+(Math.random()*0.2-0.1)})))
      }catch(e){ onToast?.(e.message) }
    })()
  },[])

  async function predict(){
    try{
      const r = await api('/api/investments/predict')
      onToast?.(`Next return (${r.model}): ${(r.next_return*100).toFixed(2)}%`)
    }catch(e){ onToast?.(e.message) }
  }

  return (
    <div className="grid">
      <div className="col-12">
        <div className="row" style={{gap:'16px'}}>
          <div className="card">
            <div className="kpi" style={{display:'flex',alignItems:'center',gap:'6px'}}>
              <span style={{fontSize:'20px'}}>₹</span> Savings
            </div>
            <div className="kpi v text-[#61D29A]">₹ {Number(kpis.savings||0).toLocaleString()}</div>
          </div>
          <div className="card">
            <div className="kpi" style={{display:'flex',alignItems:'center',gap:'6px'}}>
              <span style={{fontSize:'20px'}}>★</span> Credit Score
            </div>
            <div className="kpi v text-[#C4B5FD]">{kpis.credit_score||'-'}</div>
          </div>
          <div className="card">
            <div className="kpi" style={{display:'flex',alignItems:'center',gap:'6px'}}>
              <span style={{fontSize:'20px'}}>%</span> Returns (est.)
            </div>
            <div className="kpi v text-[#61D29A]">{((kpis.returns||0)*100).toFixed(1)}%</div>
          </div>
          <div className="card">
            <div className="kpi" style={{display:'flex',alignItems:'center',gap:'6px'}}>
              <span style={{fontSize:'20px'}}>₹</span> Tax Liability
            </div>
            <div className="kpi v text-[#ff8b8b]">₹ {Number(kpis.tax_liability||0).toLocaleString()}</div>
          </div>
        </div>
      </div>
      <div className="col-12 card">
        <h3>Portfolio Trend</h3>
        <div style={{height:320}}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series}>
              <Line type="monotone" dataKey="val" stroke="#A5B4FC" strokeWidth={3} dot={false} />
              <CartesianGrid stroke="#A5B4FC" strokeOpacity={0.2} />
              <XAxis dataKey="x" stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} style={{textShadow:'0 1px rgba(255,255,255,0.5)'}} />
              <YAxis stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} style={{textShadow:'0 1px rgba(255,255,255,0.5)'}} />
              <Tooltip contentStyle={{ background:'#2a2750', border:'1px solid #A5B4FC', color:'#FFFFFF' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3">
          <button className="btn btn-primary" onClick={predict} aria-label="Predict next return button">
            Predict Next Return <span style={{fontSize:'18px'}}>↑</span>
          </button>
        </div>
      </div>
      <div className="col-12" style={{marginTop:16}}>
        <StockPrediction onToast={onToast} />
      </div>
    </div>
  )
}
