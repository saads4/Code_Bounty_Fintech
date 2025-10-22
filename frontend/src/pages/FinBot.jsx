import React, { useState } from 'react'
import { api } from '../lib/api.js'

export default function FinBot({ onToast }){
  const [q, setQ] = useState('')
  const [chat, setChat] = useState([])
  const [example] = useState('How can I optimize my tax under the old regime?')

  async function ask(){
    if(!q.trim()) return
    try{
      const timestamp = new Date().toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'})
      const r = await api('/api/finbot/chat', { method:'POST', body: { message: q }})
      setChat([...chat, {role:'user', text:q, time:timestamp}, {role:'bot', text:r.reply, time:timestamp}])
      setQ('')
    }catch(e){ onToast?.(e.message) }
  }

  return (
    <div className="grid">
      <div className="col-12 card">
        <h3>Conversational Assistant</h3>
        <div className="stack">
          {chat.length === 0 && (
            <div 
              style={{padding:'12px',background:'rgba(165,180,252,0.05)',borderRadius:'8px',cursor:'pointer',marginBottom:'12px'}}
              onClick={()=>setQ(example)}
            >
              <div className="small" style={{marginBottom:'4px'}}>Example question (click to use):</div>
              <div style={{color:'#C4B5FD',fontStyle:'italic'}}>"{example}"</div>
            </div>
          )}
          <div style={{position:'relative'}}>
            <textarea 
              className="textarea" 
              rows="3" 
              value={q} 
              onChange={e=>setQ(e.target.value)}
              placeholder="Ask FinBot about taxes, budgets, investments..."
              style={{paddingRight:'60px'}}
              aria-label="Ask FinBot a question"
            />
            <button 
              onClick={ask}
              aria-label="Send message"
              style={{
                position:'absolute',
                right:'12px',
                bottom:'12px',
                width:'40px',
                height:'40px',
                borderRadius:'50%',
                background:'#E2E8F0',
                border:'none',
                cursor:'pointer',
                display:'flex',
                alignItems:'center',
                justifyContent:'center',
                fontSize:'20px',
                color:'#1E1B3A',
                transition:'all 0.2s'
              }}
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            >
              ↑
            </button>
          </div>
          <hr />
          <div style={{maxHeight:'400px',overflowY:'auto'}}>
            {chat.map((m,i)=>(
              <div key={i} style={{display:'flex',gap:'12px',marginBottom:'16px',alignItems:'flex-start'}}>
                <div style={{width:'32px',height:'32px',borderRadius:'50%',background:m.role==='bot'?'#8B5CF6':'#2a2750',display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0,fontSize:'16px'}}>
                  {m.role==='bot'?'🤖':'👤'}
                </div>
                <div style={{flex:1}}>
                  <div style={{background:m.role==='bot'?'rgba(139,92,246,0.1)':'rgba(165,180,252,0.1)',padding:'12px',borderRadius:'12px',marginBottom:'4px'}}>
                    {m.text}
                  </div>
                  <div className="small" style={{opacity:0.7}}>{m.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
