import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function Taxes({ onToast }){
  const [income, setIncome] = useState(1200000)
  const [deductions, setDeductions] = useState(200000)
  const [useNew, setUseNew] = useState(true)
  const [res, setRes] = useState(null)
  const [tips, setTips] = useState([])

  async function compute(){
    try{
      const r = await api('/api/taxes/compute', { method:'POST', body: { income, deductions, use_new: useNew } })
      setRes(r)
      if(!useNew){
        const s = await api('/api/taxes/suggestions/old')
        setTips(Object.entries(s))
      }else setTips([])
    }catch(e){ onToast?.(e.message) }
  }

  return (
    <div className="grid">
      <div className="col-6 card">
        <h3>Inputs</h3>
        <div className="stack">
          <div className="label">Annual Income (₹)</div>
          <input className="input" type="number" value={income} onChange={e=>setIncome(Number(e.target.value))}/>
          <div className="label">Deductions (₹) — old regime</div>
          <input className="input" type="number" value={deductions} onChange={e=>setDeductions(Number(e.target.value))}/>
          <div className="label">Regime</div>
          <select className="select" value={useNew ? 'new' : 'old'} onChange={e=>setUseNew(e.target.value==='new')}>
            <option value="new">New</option>
            <option value="old">Old</option>
          </select>
          <button className="btn" onClick={compute}>Compute Tax</button>
        </div>
      </div>

      <div className="col-6 card">
        <h3>Result</h3>
        {res ? (
          <div className="stack">
            <div>Regime: <span className="badge">{res.regime}</span></div>
            <div>Taxable Income: <b>₹ {Number(res.taxable_income).toLocaleString()}</b></div>
            <div>Tax: <b>₹ {Number(res.tax).toLocaleString()}</b></div>
            <div>Cess (4%): <b>₹ {Number(res.cess).toLocaleString()}</b></div>
            <div>Total: <b>₹ {Number(res.total).toLocaleString()}</b></div>
            <div className="small">Std Deduction: ₹ {Number(res.details.std_deduction).toLocaleString()}</div>
          </div>
        ) : <div className="small">Enter values and compute.</div>}
      </div>

      {!useNew && (
        <div className="col-12 card">
          <h3>Potential Deductions (Old Regime)</h3>
          <table><thead><tr><th>Section</th><th>Cap (₹)</th></tr></thead>
          <tbody>{tips.map(([k,v])=> <tr key={k}><td>{k}</td><td>{Number(v).toLocaleString()}</td></tr>)}</tbody></table>
        </div>
      )}
    </div>
  )
}
