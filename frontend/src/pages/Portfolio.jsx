import React, { useEffect, useState } from 'react'
import { api } from '../lib/api.js'

export default function Portfolio({ onToast }){
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newStock, setNewStock] = useState({ ticker: '', buy_price: '', quantity: '' })

  useEffect(()=>{
    fetchRecommendations()
  },[])

  async function fetchRecommendations(){
    setLoading(true)
    try{
      const data = await api('/api/portfolio/recommendations')
      setStocks(data.stocks || [])
    }catch(e){ 
      onToast?.(e.message) 
    }finally{
      setLoading(false)
    }
  }

  async function addStock(){
    if(!newStock.ticker || !newStock.buy_price || !newStock.quantity){
      onToast?.('Please fill all fields')
      return
    }
    try{
      console.log('Adding stock:', newStock)
      const result = await api('/api/portfolio/add-stock', {
        method: 'POST',
        body: {
          ticker: newStock.ticker,
          buy_price: parseFloat(newStock.buy_price),
          quantity: parseInt(newStock.quantity)
        }
      })
      console.log('Add stock result:', result)
      setNewStock({ ticker: '', buy_price: '', quantity: '' })
      setShowAddForm(false)
      onToast?.('Stock added successfully!')
      await fetchRecommendations()
    }catch(e){
      console.error('Error adding stock:', e)
      onToast?.(`Error: ${e.message}`)
    }
  }

  async function removeStock(ticker){
    try{
      await api(`/api/portfolio/remove-stock/${ticker}`, { method: 'DELETE' })
      onToast?.('Stock removed')
      fetchRecommendations()
    }catch(e){
      onToast?.(e.message)
    }
  }

  const totalProfitLoss = stocks.reduce((sum, s) => sum + s.profit_loss, 0)

  return (
    <div className="grid">
      <div className="col-12 card">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'16px'}}>
          <h2>Stock Portfolio Recommendations</h2>
          <button 
            className="btn btn-primary" 
            onClick={()=>setShowAddForm(!showAddForm)}
            aria-label="Add new stock"
          >
            {showAddForm ? 'Cancel' : '+ Add Stock'}
          </button>
        </div>

        {showAddForm && (
          <div style={{padding:'16px',background:'rgba(165,180,252,0.05)',borderRadius:'12px',marginBottom:'16px'}}>
            <h3 style={{marginTop:0}}>Add New Stock</h3>
            <div className="grid" style={{gap:'12px'}}>
              <div className="col-4">
                <label className="label">Stock Ticker (e.g., RELIANCE.NS)</label>
                <input 
                  className="input" 
                  value={newStock.ticker} 
                  onChange={e=>setNewStock({...newStock, ticker: e.target.value.toUpperCase()})}
                  placeholder="RELIANCE.NS"
                />
              </div>
              <div className="col-4">
                <label className="label">Buy Price (₹)</label>
                <input 
                  className="input" 
                  type="number" 
                  value={newStock.buy_price} 
                  onChange={e=>setNewStock({...newStock, buy_price: e.target.value})}
                  placeholder="2500"
                />
              </div>
              <div className="col-4">
                <label className="label">Quantity</label>
                <input 
                  className="input" 
                  type="number" 
                  value={newStock.quantity} 
                  onChange={e=>setNewStock({...newStock, quantity: e.target.value})}
                  placeholder="10"
                />
              </div>
            </div>
            <button className="btn btn-primary" onClick={addStock} style={{marginTop:'12px'}}>
              Add to Portfolio
            </button>
          </div>
        )}

        {loading ? (
          <div style={{textAlign:'center',padding:'40px'}}>
            <div className="skeleton" style={{height:60,width:'100%',marginBottom:12}}></div>
            <div className="skeleton" style={{height:60,width:'100%',marginBottom:12}}></div>
            <div className="skeleton" style={{height:60,width:'100%'}}></div>
          </div>
        ) : stocks.length === 0 ? (
          <div style={{textAlign:'center',padding:'40px',color:'#E2E8F0',opacity:0.7}}>
            <div style={{fontSize:'48px',marginBottom:'16px'}}>📊</div>
            <div>No stocks in portfolio. Add your first stock to get AI-powered recommendations!</div>
          </div>
        ) : (
          <>
            <div style={{marginBottom:'24px',padding:'16px',background:'rgba(165,180,252,0.1)',borderRadius:'12px'}}>
              <div style={{fontSize:'14px',color:'#E2E8F0',marginBottom:'4px'}}>Total Portfolio P&L</div>
              <div style={{fontSize:'28px',fontWeight:'bold',color:totalProfitLoss >= 0 ? '#10B981' : '#EF4444'}}>
                ₹ {totalProfitLoss.toLocaleString()} 
                <span style={{fontSize:'18px',marginLeft:'8px'}}>
                  ({totalProfitLoss >= 0 ? '+' : ''}{((totalProfitLoss / stocks.reduce((sum,s)=>sum+(s.buy_price*s.quantity),0))*100).toFixed(2)}%)
                </span>
              </div>
            </div>

            <div className="stack" style={{gap:'16px'}}>
              {stocks.map((stock, i) => (
                <div 
                  key={i} 
                  style={{
                    padding:'20px',
                    background:'rgba(165,180,252,0.05)',
                    borderRadius:'12px',
                    border:'1px solid #A5B4FC',
                    position:'relative'
                  }}
                >
                  <button
                    onClick={()=>removeStock(stock.ticker)}
                    style={{
                      position:'absolute',
                      top:'12px',
                      right:'12px',
                      background:'rgba(239,68,68,0.2)',
                      border:'1px solid #EF4444',
                      color:'#EF4444',
                      padding:'6px 12px',
                      borderRadius:'6px',
                      cursor:'pointer',
                      fontSize:'12px'
                    }}
                  >
                    Remove
                  </button>

                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'16px'}}>
                    <div>
                      <h3 style={{margin:0,fontSize:'20px',color:'#FFFFFF'}}>{stock.ticker}</h3>
                      <div style={{fontSize:'12px',color:'#E2E8F0',opacity:0.7,marginTop:'4px'}}>
                        Quantity: {stock.quantity} shares
                      </div>
                    </div>
                    <div style={{
                      padding:'8px 16px',
                      background: stock.recommendation === 'BUY' ? 'rgba(16,185,129,0.2)' : 
                                 stock.recommendation === 'SELL' ? 'rgba(239,68,68,0.2)' : 
                                 'rgba(165,180,252,0.2)',
                      border: stock.recommendation === 'BUY' ? '1px solid #10B981' : 
                             stock.recommendation === 'SELL' ? '1px solid #EF4444' : 
                             '1px solid #A5B4FC',
                      borderRadius:'8px',
                      fontSize:'16px',
                      fontWeight:'bold',
                      color: stock.recommendation === 'BUY' ? '#10B981' : 
                            stock.recommendation === 'SELL' ? '#EF4444' : 
                            '#C4B5FD'
                    }}>
                      {stock.emoji} {stock.recommendation}
                    </div>
                  </div>

                  <div className="grid" style={{gap:'16px'}}>
                    <div className="col-3">
                      <div style={{fontSize:'12px',color:'#E2E8F0',opacity:0.7}}>Buy Price</div>
                      <div style={{fontSize:'18px',fontWeight:'bold',color:'#FFFFFF'}}>₹ {stock.buy_price.toLocaleString()}</div>
                    </div>
                    <div className="col-3">
                      <div style={{fontSize:'12px',color:'#E2E8F0',opacity:0.7}}>Current Price</div>
                      <div style={{fontSize:'18px',fontWeight:'bold',color:'#C4B5FD'}}>₹ {stock.current_price.toLocaleString()}</div>
                    </div>
                    <div className="col-3">
                      <div style={{fontSize:'12px',color:'#E2E8F0',opacity:0.7}}>P&L</div>
                      <div style={{fontSize:'18px',fontWeight:'bold',color: stock.profit_loss >= 0 ? '#10B981' : '#EF4444'}}>
                        ₹ {stock.profit_loss.toLocaleString()} ({stock.profit_loss >= 0 ? '+' : ''}{stock.profit_loss_pct.toFixed(2)}%)
                      </div>
                    </div>
                    <div className="col-3">
                      <div style={{fontSize:'12px',color:'#E2E8F0',opacity:0.7}}>News Sentiment</div>
                      <div style={{fontSize:'18px',fontWeight:'bold',color: stock.sentiment > 0 ? '#10B981' : stock.sentiment < 0 ? '#EF4444' : '#E2E8F0'}}>
                        {stock.sentiment > 0 ? '😊' : stock.sentiment < 0 ? '😟' : '😐'} {stock.sentiment.toFixed(3)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button 
              className="btn btn-secondary" 
              onClick={fetchRecommendations}
              style={{marginTop:'24px',width:'100%'}}
              aria-label="Refresh recommendations"
            >
              🔄 Refresh Recommendations
            </button>
          </>
        )}
      </div>

      <div className="col-12 card">
        <h3>How It Works</h3>
        <div className="stack" style={{gap:'12px'}}>
          <div style={{display:'flex',gap:'12px',alignItems:'flex-start'}}>
            <div style={{fontSize:'24px'}}>📊</div>
            <div>
              <div style={{fontWeight:'bold',color:'#C4B5FD'}}>Real-time Analysis</div>
              <div style={{fontSize:'14px',color:'#E2E8F0',opacity:0.9}}>
                Fetches latest stock prices and calculates technical indicators (Returns, MA5, MA20)
              </div>
            </div>
          </div>
          <div style={{display:'flex',gap:'12px',alignItems:'flex-start'}}>
            <div style={{fontSize:'24px'}}>📰</div>
            <div>
              <div style={{fontWeight:'bold',color:'#C4B5FD'}}>News Sentiment</div>
              <div style={{fontSize:'14px',color:'#E2E8F0',opacity:0.9}}>
                Analyzes recent news headlines using NLP to gauge market sentiment (-1 to +1)
              </div>
            </div>
          </div>
          <div style={{display:'flex',gap:'12px',alignItems:'flex-start'}}>
            <div style={{fontSize:'24px'}}>🤖</div>
            <div>
              <div style={{fontWeight:'bold',color:'#C4B5FD'}}>ML Prediction</div>
              <div style={{fontSize:'14px',color:'#E2E8F0',opacity:0.9}}>
                Trained ML model combines price trends and sentiment to recommend BUY 📈, SELL 📉, or HOLD 🤔
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
