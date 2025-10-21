import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function FinBot({ onToast }){
  const [q, setQ] = useState('How can I optimize my tax under the old regime?')
  const [chat, setChat] = useState([])

  async function ask(){
    try{
      const r = await api('/api/finbot/chat', { method:'POST', body: { message: q }})
      setChat([...chat, {role:'user', text:q}, {role:'bot', text:r.reply}])
      setQ('')
    }catch(e){ onToast?.(e.message) }
  }

  return (
    <div className="grid">
      <div className="col-12 card">
        <h3>Conversational Assistant</h3>
        <div className="stack">
          <textarea className="textarea" rows="3" value={q} onChange={e=>setQ(e.target.value)} />
          <div><button className="btn" onClick={ask}>Ask FinBot</button></div>
          <hr />
          <div>
            {chat.map((m,i)=>(<div key={i} style={{marginBottom:8}}><b>{m.role==='user'?'You':'FinBot'}:</b> {m.text}</div>))}
          </div>
        </div>
      </div>
    </div>
  )
}
