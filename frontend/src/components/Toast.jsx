// frontend/src/components/Toast.jsx
import React, { useEffect } from 'react'

export default function Toast({ message, type='info', onClose, autoHideMs=3000 }){
  useEffect(()=>{
    if(!message) return
    const t = setTimeout(()=> onClose?.(), autoHideMs)
    return ()=> clearTimeout(t)
  }, [message, autoHideMs, onClose])

  if(!message) return null
  return (
    <div className={`toast toast--${type}`} role="status" onClick={onClose}>
      {message}
    </div>
  )
}
