import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

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
        <div className="row">
          <div className="card"><div className="kpi">Savings</div><div className="kpi v">₹ {Number(kpis.savings||0).toLocaleString()}</div></div>
          <div className="card"><div className="kpi">Credit Score</div><div className="kpi v">{kpis.credit_score||'-'}</div></div>
          <div className="card"><div className="kpi">Returns (est.)</div><div className="kpi v">{((kpis.returns||0)*100).toFixed(1)}%</div></div>
          <div className="card"><div className="kpi">Tax Liability</div><div className="kpi v">₹ {Number(kpis.tax_liability||0).toLocaleString()}</div></div>
        </div>
      </div>
      <div className="col-12 card">
        <h3>Portfolio Trend</h3>
        <div style={{height:320}}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series}>
              <Line type="monotone" dataKey="val" />
              <CartesianGrid stroke="#22305a" />
              <XAxis dataKey="x" />
              <YAxis />
              <Tooltip />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div style={{marginTop:12}}>
          <button className="btn" onClick={predict}>Predict Next Return</button>
        </div>
      </div>
    </div>
  )
}
