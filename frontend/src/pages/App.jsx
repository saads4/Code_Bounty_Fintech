// frontend/src/pages/App.jsx
import React, { useEffect, useState } from 'react'
import Dashboard from './Dashboard.jsx'
import Budget from './Budget.jsx'
import Credit from './Credit.jsx'
import Taxes from './Taxes.jsx'
import FinBot from './FinBot.jsx'
import StockMind from './StockMind.jsx'
import Profile from './Profile.jsx'
import Login from './Login.jsx'
import Toast from '../components/Toast.jsx'
import { logout, ensureAuth } from '../lib/api.js'

const TABS = ['Dashboard','Budget','Credit','Taxes','StockMind','FinBot','Profile']

export default function App(){
  const [tab, setTab] = useState('Dashboard')
  const [toast, setToast] = useState('')
  const [authed, setAuthed] = useState(false)

  useEffect(()=>{
    (async ()=>{
      try{
        // Proactively ensure a valid token at app start
        await ensureAuth();
        setAuthed(true);
      }catch(_){
        setAuthed(false);
      }
    })()
  },[])

  if(!authed){
    return <Login onLoggedIn={()=>setAuthed(true)} onToast={setToast} />
  }

  return (
    <>
      <div className="header">
        <div className="header-inner">
          <div className="title">FinEdge Pro</div>
          <div>
            <button className="btn btn-secondary" onClick={()=>{ logout(); setAuthed(false); setToast('Signed out'); }}>Logout</button>
          </div>
        </div>
      </div>
      <div className="container">
        <div className="small">AI-powered personal finance • India tax ready • ML insights</div>
        <div className="nav" style={{marginTop:16}}>
          {TABS.map(t => (
            <div
              key={t}
              className={'tab' + (tab===t?' active':'') + ' hover:brightness-110 focus:outline-none'}
              onClick={()=>setTab(t)}
            >
              <span style={{opacity: tab===t ? 1 : 0.95, fontWeight: tab===t ? 600 : 500}}>{t}</span>
            </div>
          ))}
        </div>

        <div style={{marginTop:16}}>
          {tab==='Dashboard' && <Dashboard onToast={setToast}/>}
          {tab==='Budget' && <Budget onToast={setToast}/>}
          {tab==='Credit' && <Credit onToast={setToast}/>}
          {tab==='Taxes' && <Taxes onToast={setToast}/>}
          {tab==='StockMind' && <StockMind onToast={setToast}/>}
          {tab==='FinBot' && <FinBot onToast={setToast}/>}
          {tab==='Profile' && <Profile onToast={setToast}/>}
        </div>
        <div className="footer">API docs: <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></div>
      </div>
      <Toast message={toast} onClose={()=>setToast('')} type="info" />
    </>
  )
}
