import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export default function Credit({ onToast }){
  const [metrics, setMetrics] = useState(null)
  const [form, setForm] = useState({ income:600000, age:25, utilization:0.35, late_pay:0, dti:0.25 })
  const [score, setScore] = useState(null)

  useEffect(()=>{ api('/api/credit/metrics').then(setMetrics).catch(e=>onToast?.(e.message)) },[])

  async function runScore(){ try{ setScore(await api('/api/credit/score', { method:'POST', body: form })) }catch(e){ onToast?.(e.message) } }

  const shapData = (score?.shap?.features||[]).map((f, i)=>({ name:f, value: (score?.shap?.values||[])[i]||0 }))

  return (
    <div className="grid">
      <div className="col-6 card">
        <h3>Model Metrics</h3>
        {metrics ? (
          <div className="stack">
            <div>AUC (Logistic Regression): <span className="badge" style={{borderColor:'#36d399', color:'#36d399'}}>{metrics.auc_lr.toFixed(3)}</span></div>
            <div>AUC (Random Forest): <span className="badge" style={{borderColor:'#6ea8fe', color:'#6ea8fe'}}>{metrics.auc_rf.toFixed(3)}</span></div>
          </div>
        ) : <div className="small">Loading metrics…</div>}
      </div>

      <div className="col-6 card">
        <h3>Input Features</h3>
        {Object.keys(form).map(k=>(
          <div key={k} className="stack">
            <div className="label">{k}</div>
            <input className="input" type="number" step="any" value={form[k]} onChange={e=>setForm({...form,[k]:Number(e.target.value)})} />
          </div>
        ))}
        <div className="mt-2"><button className="btn btn-primary" onClick={runScore}>Score Credit Risk</button></div>
      </div>

      <div className="col-12 card">
        <h3>Default Probability & SHAP Explanation</h3>
        {score ? (
          <>
            <div className="badge" style={{borderColor:'#ff8b8b', color:'#ff8b8b'}}>Probability of Default: {(score.prob_default*100).toFixed(2)}%</div>
            <div style={{height:320, marginTop:12}}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shapData}>
                  <CartesianGrid stroke="#22305a" />
                  <XAxis dataKey="name" stroke="#aeb7d4" tick={{ fill:'#aeb7d4' }} />
                  <YAxis stroke="#aeb7d4" tick={{ fill:'#aeb7d4' }} />
                  <Tooltip contentStyle={{ background:'#121a33', border:'1px solid #22305a', color:'#e8ecff' }} />
                  <Bar dataKey="value" fill="#7a5af5" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : <div className="small">Enter features and click score.</div>}
      </div>
    </div>
  )
}
