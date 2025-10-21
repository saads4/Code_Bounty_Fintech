// frontend/src/pages/App.jsx
import React, { useEffect, useState } from 'react'
import Dashboard from './Dashboard.jsx'
import Budget from './Budget.jsx'
import Credit from './Credit.jsx'
import Taxes from './Taxes.jsx'
import FinBot from './FinBot.jsx'
import Login from './Login.jsx'
import { logout } from '../lib/api.js'

const TABS = ['Dashboard','Budget','Credit','Taxes','FinBot']

export default function App(){
  const [tab, setTab] = useState('Dashboard')
  const [toast, setToast] = useState('')
  const [authed, setAuthed] = useState(false)

  useEffect(()=>{
    const t = localStorage.getItem('token')
    setAuthed(!!t)
  },[])

  if(!authed){
    return <Login onLoggedIn={()=>setAuthed(true)} onToast={setToast} />
  }

  return (
    <div className="container">
      <h1>FinEdge Pro</h1>
      <div className="small">AI-powered personal finance • India tax ready • ML insights</div>
      <div style={{marginTop:8, display:'flex', justifyContent:'flex-end'}}>
        <button className="btn" onClick={()=>{ logout(); setAuthed(false); setToast('Signed out'); }}>Logout</button>
      </div>
      <div className="nav" style={{marginTop:16}}>
        {TABS.map(t => (
          <div key={t} className={'tab' + (tab===t?' active':'')} onClick={()=>setTab(t)}>{t}</div>
        ))}
      </div>

      <div style={{marginTop:16}}>
        {tab==='Dashboard' && <Dashboard onToast={setToast}/>}
        {tab==='Budget' && <Budget onToast={setToast}/>}
        {tab==='Credit' && <Credit onToast={setToast}/>}
        {tab==='Taxes' && <Taxes onToast={setToast}/>}
        {tab==='FinBot' && <FinBot onToast={setToast}/>}
      </div>

      {toast && <div className="toast" onClick={()=>setToast('')}>{toast}</div>}

      <div className="footer">API docs: <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></div>
    </div>
  )
}
