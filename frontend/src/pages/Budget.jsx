import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function Budget({ onToast }){
  const [items, setItems] = useState([
    { description:'Milk and vegetables from supermarket', amount: 650, type:'expense' },
    { description:'Uber ride to office', amount: 220, type:'expense' },
    { description:'Monthly salary', amount: 50000, type:'income' },
  ])
  const [categorized, setCategorized] = useState([])
  const [reco, setReco] = useState(null)

  const update = (i, key, val)=>{ const next = items.slice(); next[i][key]=val; setItems(next) }
  const add = ()=> setItems([...items, { description:'', amount:0, type:'expense' }])
  const del = (i)=> setItems(items.filter((_,k)=>k!==i))

  async function runCategorize(){ try{ setCategorized((await api('/api/budget/categorize',{method:'POST', body: items})).items) }catch(e){ onToast?.(e.message) } }
  async function runRecommend(){ try{ setReco(await api('/api/budget/recommend',{method:'POST', body: items})) }catch(e){ onToast?.(e.message) } }

  return (
    <div className="grid">
      <div className="col-12 card">
        <h3>Expense & Income Items</h3>
        <table>
          <thead><tr><th>Description</th><th>Amount</th><th>Type</th><th></th></tr></thead>
          <tbody>
            {items.map((it,i)=>(
              <tr key={i}>
                <td><input className="input" value={it.description} onChange={e=>update(i,'description',e.target.value)} /></td>
                <td><input className="input" type="number" value={it.amount} onChange={e=>update(i,'amount',Number(e.target.value))} /></td>
                <td>
                  <select className="select" value={it.type} onChange={e=>update(i,'type',e.target.value)}>
                    <option value="expense">expense</option>
                    <option value="income">income</option>
                  </select>
                </td>
                <td><button className="btn btn-secondary" onClick={()=>del(i)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-2 flex gap-2">
          <button className="btn btn-secondary" onClick={add}>Add Row</button>
          <button className="btn btn-primary" onClick={runCategorize}>Categorize</button>
          <button className="btn btn-primary" onClick={runRecommend}>Recommend Budgets</button>
        </div>
      </div>

      <div className="col-6 card">
        <h3>Categorization</h3>
        <table>
          <thead><tr><th>Description</th><th>Predicted Category</th></tr></thead>
          <tbody>
            {categorized.map((it,i)=>(
              <tr key={i}>
                <td>{it.description}</td>
                <td><span className="badge" style={{borderColor:'#3856a1', color:'#6ea8fe'}}>{it.category_pred}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="col-6 card">
        <h3>50/30/20 Recommendation</h3>
        {reco ? (
          <div className="stack">
            <div>Monthly Income: <b>₹ {Number(reco.monthly_income||0).toLocaleString()}</b></div>
            <div>Essentials: <span className="badge" style={{borderColor:'#7a5af5', color:'#bda7ff'}}>₹ {Number(reco.suggested.essentials).toLocaleString()}</span></div>
            <div>Wants: <span className="badge" style={{borderColor:'#fbbf24', color:'#fbbf24'}}>₹ {Number(reco.suggested.wants).toLocaleString()}</span></div>
            <div>Savings: <span className="badge" style={{borderColor:'#36d399', color:'#36d399'}}>₹ {Number(reco.suggested.savings).toLocaleString()}</span></div>
          </div>
        ) : <div className="small">Click “Recommend Budgets”.</div>}
      </div>
    </div>
  )
}
