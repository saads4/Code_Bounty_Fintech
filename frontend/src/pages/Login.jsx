// frontend/src/pages/Login.jsx
import React, { useState } from 'react'
import { register as apiRegister, login as apiLogin } from '../lib/api.js'

export default function Login({ onLoggedIn, onToast }){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e){
    e.preventDefault()
    setLoading(true)
    try{
      if(mode === 'register'){
        await apiRegister(email, password, fullName)
      }else{
        await apiLogin(email, password)
      }
      onLoggedIn?.()
    }catch(err){
      onToast?.(String(err.message || err))
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>FinEdge Pro</h1>
      <div className="small">{mode==='login' ? 'Sign in to continue' : 'Create your account'}</div>
      <form onSubmit={handleSubmit} style={{marginTop:16, maxWidth:360}}>
        {mode==='register' && (
          <div className="form-row">
            <label>Full name</label>
            <input type="text" value={fullName} onChange={e=>setFullName(e.target.value)} placeholder="Your Name" />
          </div>
        )}
        <div className="form-row">
          <label>Email</label>
          <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" required />
        </div>
        <div className="form-row">
          <label>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••" required />
        </div>
        <button type="submit" disabled={loading} className="btn">
          {loading ? (mode==='login' ? 'Signing in…' : 'Creating account…') : (mode==='login' ? 'Sign In' : 'Create Account')}
        </button>
      </form>
      <div className="small" style={{marginTop:12}}>
        {mode==='login' ? (
          <>
            New here? <a href="#" onClick={(e)=>{e.preventDefault(); setMode('register')}}>Create an account</a>
          </>
        ) : (
          <>
            Already have an account? <a href="#" onClick={(e)=>{e.preventDefault(); setMode('login')}}>Sign in</a>
          </>
        )}
      </div>
    </div>
  )
}
