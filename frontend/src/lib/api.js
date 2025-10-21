// frontend/src/lib/api.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function getToken(){ return localStorage.getItem('token') || ''; }

async function ensureAuth(email='demo@demo.com', password='demo123'){
  const t = getToken();
  if(t) return t;
  // try register, else login
  const h = { 'Content-Type':'application/json' };
  try{
    const r = await fetch(`${API_BASE}/api/auth/register`, {
      method:'POST', headers:h,
      body: JSON.stringify({ email, password, full_name:'Demo User' })
    });
    if(!r.ok) throw new Error(await r.text());
    const data = await r.json();
    localStorage.setItem('token', data.access_token);
    return data.access_token;
  }catch(_){
    const r2 = await fetch(`${API_BASE}/api/auth/login`, {
      method:'POST', headers:h,
      body: JSON.stringify({ email, password })
    });
    if(!r2.ok) throw new Error(await r2.text());
    const data2 = await r2.json();
    localStorage.setItem('token', data2.access_token);
    return data2.access_token;
  }
}

// One-shot retry on 401: acquire token then retry the same call
async function api(path, { method='GET', body, headers={} } = {}, _retried=false){
  const h = { 'Content-Type':'application/json', ...headers };
  const token = getToken();
  if(token) h['Authorization'] = 'Bearer ' + token;

  const res = await fetch(`${API_BASE}${path}`, { method, headers: h, body: body ? JSON.stringify(body) : undefined });

  // If 401 and we haven’t retried yet, ensure auth then retry once
  if(res.status === 401 && !_retried){
    await ensureAuth();
    return api(path, { method, body, headers }, true);
  }

  if(!res.ok){
    const txt = await res.text().catch(()=> '');
    throw new Error(`API ${method} ${path} -> ${res.status}: ${txt || res.statusText}`);
  }

  const ct = res.headers.get('content-type') || '';
  if(ct.includes('application/json')) return res.json();
  return res;
}

export { API_BASE, api, ensureAuth };
