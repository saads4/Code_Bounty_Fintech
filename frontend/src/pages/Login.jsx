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
    <div className="min-h-screen bg-[#0b1020] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">FinEdge Pro</h1>
          <p className="text-sm text-[#aeb7d4] mt-1">{mode==='login' ? 'Sign in to continue' : 'Create your account'}</p>
        </div>
        <div className="rounded-2xl border border-[#22305a] bg-[#121a33] shadow-card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode==='register' && (
              <div>
                <label className="block text-xs text-[#aeb7d4] mb-1">Full name</label>
                <input className="input focus:outline-none w-full" type="text" value={fullName} onChange={e=>setFullName(e.target.value)} placeholder="Your Name" />
              </div>
            )}
            <div>
              <label className="block text-xs text-[#aeb7d4] mb-1">Email</label>
              <input className="input focus:outline-none w-full" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" required />
            </div>
            <div>
              <label className="block text-xs text-[#aeb7d4] mb-1">Password</label>
              <input className="input focus:outline-none w-full" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••" required />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary w-full">
              {loading ? (mode==='login' ? 'Signing in…' : 'Creating account…') : (mode==='login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>
          <div className="text-xs text-[#aeb7d4] mt-3 text-center">
            {mode==='login' ? (
              <>
                New here? <a className="text-[#6ea8fe] hover:underline" href="#" onClick={(e)=>{e.preventDefault(); setMode('register')}}>Create an account</a>
              </>
            ) : (
              <>
                Already have an account? <a className="text-[#6ea8fe] hover:underline" href="#" onClick={(e)=>{e.preventDefault(); setMode('login')}}>Sign in</a>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
