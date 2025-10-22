// frontend/src/pages/Profile.jsx
import React, { useEffect, useState } from 'react'
import { getMe, updateMe } from '../lib/api.js'

export default function Profile({ onToast }){
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  useEffect(()=>{
    (async ()=>{
      try{
        const me = await getMe()
        setEmail(me.email || '')
        setFullName(me.full_name || '')
      }catch(err){
        onToast?.(String(err.message || err))
      }finally{
        setLoading(false)
      }
    })()
  },[])

  async function handleSave(e){
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    try{
      const body = { full_name: fullName }
      if(password) body.password = password
      const updated = await updateMe(body)
      setFullName(updated.full_name || '')
      setPassword('')
      setSaved(true)
      onToast?.('Profile updated!')
      setTimeout(()=>setSaved(false), 3000)
    }catch(err){
      onToast?.(String(err.message || err))
    }finally{
      setSaving(false)
    }
  }

  if(loading){
    return (
      <div className="card">
        <h2>Your Profile</h2>
        <div className="skeleton" style={{height:12, width:180, marginTop:8}}></div>
        <div className="skeleton" style={{height:12, width:240, marginTop:8}}></div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>Your Profile</h2>
      <form onSubmit={handleSave} className="space-y-4 mt-3 max-w-xl">
        <div>
          <label className="block text-xs text-[#9CA3AF] mb-1" style={{fontStyle:'italic'}}>Email (read-only)</label>
          <div style={{position:'relative'}}>
            <input className="input" type="email" value={email} readOnly />
            <button 
              type="button"
              onClick={()=>{navigator.clipboard.writeText(email);onToast?.('Email copied!')}}
              style={{position:'absolute',right:'10px',top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',fontSize:'16px'}}
              aria-label="Copy email to clipboard"
            >
              📋
            </button>
          </div>
        </div>
        <div>
          <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>Full name</label>
          <input className="input" type="text" value={fullName} onChange={e=>setFullName(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-[#E2E8F0] mb-1" style={{opacity:0.9}}>New Password</label>
          <div style={{position:'relative'}}>
            <input className="input" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder="Leave blank to keep current" />
            <button 
              type="button"
              onClick={()=>setShowPassword(!showPassword)}
              style={{position:'absolute',right:'10px',top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',fontSize:'16px'}}
              aria-label="Toggle password visibility"
            >
              {showPassword?'👁️':'👁️‍🗨️'}
            </button>
          </div>
        </div>
        <button 
          type="submit" 
          className="btn" 
          style={{background:saved?'#10B981':'linear-gradient(135deg,#A78BFA,#8B5CF6)',borderColor:saved?'#10B981':'#8B5CF6',color:'#FFFFFF'}}
          disabled={saving}
          aria-label="Save profile changes"
        >
          {saving ? 'Saving…' : saved ? '✓ Saved!' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
