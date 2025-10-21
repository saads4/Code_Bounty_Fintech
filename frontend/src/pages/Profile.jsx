// frontend/src/pages/Profile.jsx
import React, { useEffect, useState } from 'react'
import { getMe, updateMe } from '../lib/api.js'

export default function Profile({ onToast }){
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')

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
    try{
      const body = { full_name: fullName }
      if(password) body.password = password
      const updated = await updateMe(body)
      setFullName(updated.full_name || '')
      setPassword('')
      onToast?.('Profile updated')
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
          <label className="block text-xs text-[#aeb7d4] mb-1">Email (read-only)</label>
          <input className="input" type="email" value={email} readOnly />
        </div>
        <div>
          <label className="block text-xs text-[#aeb7d4] mb-1">Full name</label>
          <input className="input" type="text" value={fullName} onChange={e=>setFullName(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-[#aeb7d4] mb-1">New password (optional)</label>
          <input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Leave blank to keep current" />
        </div>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
