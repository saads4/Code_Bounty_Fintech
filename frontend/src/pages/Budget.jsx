import React, { useState, useMemo } from 'react'
import { api } from '../lib/api.js'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

export default function Budget({ onToast }){
  const [items, setItems] = useState([
    { description:'Milk and vegetables from supermarket', amount: 650, type:'expense' },
    { description:'Uber ride to office', amount: 220, type:'expense' },
    { description:'Monthly salary', amount: 50000, type:'income' },
  ])
  const [categorized, setCategorized] = useState([])
  const [reco, setReco] = useState(null)

  // Color scheme
  const COLORS = ['#A5B4FC', '#C4B5FD', '#61D29A', '#E2E8F0']

  // Process categorization data for pie chart
  const categoryChartData = useMemo(() => {
    const categoryTotals = {}
    categorized.forEach(item => {
      const category = item.category_pred || 'Uncategorized'
      const amount = Number(item.amount) || 0
      categoryTotals[category] = (categoryTotals[category] || 0) + amount
    })
    return Object.entries(categoryTotals).map(([name, value]) => ({ name, value }))
  }, [categorized, items])

  // Process recommendation data for pie chart
  const recoChartData = useMemo(() => {
    if (!reco) return []
    return [
      { name: 'Essentials (50%)', value: reco.suggested.essentials },
      { name: 'Wants (30%)', value: reco.suggested.wants },
      { name: 'Savings (20%)', value: reco.suggested.savings }
    ]
  }, [reco])

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
          <button className="btn btn-secondary" onClick={add} aria-label="Add new expense row">Add Row</button>
          <button className="btn btn-primary" onClick={runCategorize} aria-label="Categorize expenses">Categorize</button>
          <button className="btn btn-primary" onClick={runRecommend} aria-label="Get budget recommendations">Recommend Budgets</button>
        </div>
      </div>

      <div className="col-6 card">
        <h3>Categorization</h3>
        {categorized.length > 0 && categoryChartData.length > 0 ? (
          <div className="stack">
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ value }) => `₹${value.toLocaleString()}`}
                >
                  {categoryChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend 
                  verticalAlign="bottom" 
                  height={50}
                  wrapperStyle={{color:'#E2E8F0',fontWeight:'bold'}}
                  iconType="square"
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4">
              <table>
                <thead><tr><th>Description</th><th>Predicted Category</th></tr></thead>
                <tbody>
                  {categorized.map((it,i)=>(
                    <tr key={i}>
                      <td>{it.description}</td>
                      <td><span className="badge" style={{borderColor:'#A5B4FC', color:'#C4B5FD'}}>{it.category_pred}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="small">Click "Categorize" to see results.</div>
        )}
      </div>

      <div className="col-6 card">
        <h3>50/30/20 Recommendation</h3>
        {reco ? (
          <div className="stack">
            <div className="mb-2">Monthly Income: <b>₹ {Number(reco.monthly_income||0).toLocaleString()}</b></div>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={recoChartData}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ value }) => `₹${value.toLocaleString()}`}
                >
                  {recoChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend 
                  verticalAlign="bottom" 
                  height={50}
                  wrapperStyle={{color:'#E2E8F0',fontWeight:'bold'}}
                  iconType="square"
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 stack">
              <div>Essentials: <span className="badge" style={{borderColor:'#A5B4FC', color:'#C4B5FD'}}>₹ {Number(reco.suggested.essentials).toLocaleString()}</span></div>
              <div>Wants: <span className="badge" style={{borderColor:'#C4B5FD', color:'#C4B5FD'}}>₹ {Number(reco.suggested.wants).toLocaleString()}</span></div>
              <div>Savings: <span className="badge" style={{borderColor:'#61D29A', color:'#61D29A'}}>₹ {Number(reco.suggested.savings).toLocaleString()}</span></div>
            </div>
          </div>
        ) : <div className="small">Click "Recommend Budgets".</div>}
      </div>
    </div>
  )
}
