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
          <div className="label">Regime <span style={{fontSize:'14px'}}>⇄</span></div>
          <select className="select" value={useNew ? 'new' : 'old'} onChange={e=>setUseNew(e.target.value==='new')} style={{marginRight:'8px'}} aria-label="Select tax regime">
            <option value="new">✨ New Regime</option>
            <option value="old">📜 Old Regime</option>
          </select>
          <button className="btn btn-primary" onClick={compute} aria-label="Compute tax">Compute Tax</button>
        </div>
      </div>

      <div className="col-6 card">
        <h3>Result</h3>
        {res ? (
          <div className="stack">
            <div style={{padding:'12px',background:'rgba(165,180,252,0.1)',borderRadius:'8px',marginBottom:'12px'}}>
              <div style={{fontSize:'14px',color:'#E2E8F0',marginBottom:'4px'}}>Regime</div>
              <div style={{fontSize:'16px',fontWeight:'bold',color:'#C4B5FD'}}>{res.regime}</div>
            </div>
            <details style={{marginBottom:'12px'}}>
              <summary style={{cursor:'pointer',fontWeight:'bold',color:'#A5B4FC',marginBottom:'8px'}}>Breakdown</summary>
              <div className="stack" style={{paddingLeft:'16px',marginTop:'8px'}}>
                <div>Taxable Income: <b style={{color:'#C4B5FD'}}>₹ {Number(res.taxable_income).toLocaleString()}</b></div>
                <div className="small">Std Deduction: ₹ {Number(res.details.std_deduction).toLocaleString()}</div>
              </div>
            </details>
            <div style={{fontSize:'18px'}}>Tax: <b style={{color:'#EF4444'}}>₹ {Number(res.tax).toLocaleString()}</b></div>
            <div style={{fontSize:'18px'}}>Cess (4%): <b style={{color:'#10B981'}}>₹ {Number(res.cess).toLocaleString()}</b></div>
            <div style={{fontSize:'20px',fontWeight:'bold',marginTop:'8px',padding:'12px',background:'rgba(16,185,129,0.1)',borderRadius:'8px'}}>Total: <span style={{color:'#10B981'}}>₹ {Number(res.total).toLocaleString()}</span></div>
          </div>
        ) : <div className="small">Enter values and compute.</div>}
      </div>

      {!useNew && (
        <div className="col-12 card">
          <h3>Potential Deductions (Old Regime)</h3>
          <table>
            <thead><tr><th>Section</th><th>Cap (₹)</th></tr></thead>
            <tbody>{tips.map(([k,v])=> <tr key={k}><td>{k}</td><td><span className="badge" style={{borderColor:'#7a5af5', color:'#bda7ff'}}>{Number(v).toLocaleString()}</span></td></tr>)}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
