import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export default function Credit({ onToast }){
  const [form, setForm] = useState({ income:600000, age:25, utilization:0.35, late_pay:0, dti:0.25 })
  const [score, setScore] = useState(null)

  async function runScore(){ try{ setScore(await api('/api/credit/score', { method:'POST', body: form })) }catch(e){ onToast?.(e.message) } }

  const shapData = (score?.shap?.features||[]).map((f, i)=>({ name:f, value: (score?.shap?.values||[])[i]||0 }))

  return (
    <div className="grid">
      <div className="col-6 card">
        <h3>Input Features</h3>
        {Object.keys(form).map((k,i)=>(
          <div key={k} className="stack" style={{background:i%2===0?'rgba(165,180,252,0.05)':'transparent',padding:'8px',borderRadius:'6px',borderBottom:'1px solid rgba(67,56,202,0.3)'}}>
            <div className="label">{k}</div>
            <input className="input" type="number" step="any" value={form[k]} onChange={e=>setForm({...form,[k]:Number(e.target.value)})} />
          </div>
        ))}
        <div className="mt-2" style={{alignSelf:'flex-start'}}>
          <button className="btn btn-primary" onClick={runScore} aria-label="Score credit risk button">
            Score Credit Risk
          </button>
        </div>
      </div>

      <div className="col-12 card">
        <h3>Default Probability & SHAP Explanation</h3>
        {score ? (
          <>
            <div style={{marginBottom:'16px'}}>
              <div style={{fontWeight:'bold',fontSize:'18px',marginBottom:'8px'}}>Probability of Default: <span style={{color:'#ff8b8b'}}>{(score.prob_default*100).toFixed(2)}%</span></div>
              <div style={{width:'100%',height:'24px',background:'#1E1B3A',borderRadius:'12px',overflow:'hidden',border:'1px solid #A5B4FC'}}>
                <div style={{width:`${(score.prob_default*100).toFixed(2)}%`,height:'100%',background:'linear-gradient(to right, #A78BFA, #8B5CF6)',transition:'width 0.3s ease'}}></div>
              </div>
            </div>
            <div style={{height:320, marginTop:12}}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shapData}>
                  <CartesianGrid stroke="#A5B4FC" strokeOpacity={0.2} />
                  <XAxis dataKey="name" stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} />
                  <YAxis stroke="#E2E8F0" tick={{ fill:'#E2E8F0', fontSize:12 }} />
                  <Tooltip contentStyle={{ background:'#2a2750', border:'1px solid #A5B4FC', color:'#FFFFFF' }} />
                  <Bar dataKey="value" fill="#A78BFA" stroke="#FFFFFF" strokeWidth={1} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : <div className="small">Enter features and click score.</div>}
      </div>
    </div>
  )
}
