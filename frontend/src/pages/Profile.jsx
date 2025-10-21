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
      <div>
        <h2>Your Profile</h2>
        <div className="small">Loading…</div>
      </div>
    )
  }

  return (
    <div>
      <h2>Your Profile</h2>
      <form onSubmit={handleSave} style={{maxWidth:480, marginTop:12}}>
        <div className="form-row">
          <label>Email (read-only)</label>
          <input type="email" value={email} readOnly />
        </div>
        <div className="form-row">
          <label>Full name</label>
          <input type="text" value={fullName} onChange={e=>setFullName(e.target.value)} />
        </div>
        <div className="form-row">
          <label>New password (optional)</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Leave blank to keep current" />
        </div>
        <button type="submit" className="btn" disabled={saving}>
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
