import { useState } from 'react'
import { Activity, Beaker, ClipboardList, Send, AlertTriangle, CheckCircle } from 'lucide-react'

function App() {
  const [formData, setFormData] = useState({
    age: 48, bp: 80, sg: 1.020, al: 1, su: 0,
    rbc: 'normal', pc: 'normal', pcc: 'notpresent', ba: 'notpresent',
    bgr: 121, bu: 36, sc: 1.2, sod: 137, pot: 4.6,
    hemo: 15.4, pcv: 44, wc: 7800, rc: 5.2,
    htn: 'yes', dm: 'yes', cad: 'no', appet: 'good', pe: 'no', ane: 'no'
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)
    
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (!response.ok) throw new Error('API request failed')
      
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Could not connect to the prediction server. Please ensure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>CKD Predictor</h1>
      <p className="subtitle">Advanced Neural Analysis for Chronic Kidney Disease</p>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {/* Numeric Fields */}
            <div className="input-group">
              <label>Age</label>
              <input type="number" name="age" value={formData.age} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Blood Pressure (bp)</label>
              <input type="number" name="bp" value={formData.bp} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Specific Gravity (sg)</label>
              <input type="number" step="0.001" name="sg" value={formData.sg} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Albumin (al)</label>
              <input type="number" name="al" value={formData.al} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Sugar (su)</label>
              <input type="number" name="su" value={formData.su} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>Hemoglobin (hemo)</label>
              <input type="number" step="0.1" name="hemo" value={formData.hemo} onChange={handleChange} />
            </div>
            
            {/* Categorical Fields */}
            <div className="input-group">
              <label>Red Blood Cells</label>
              <select name="rbc" value={formData.rbc} onChange={handleChange}>
                <option value="normal">Normal</option>
                <option value="abnormal">Abnormal</option>
              </select>
            </div>
            <div className="input-group">
              <label>Hypertension</label>
              <select name="htn" value={formData.htn} onChange={handleChange}>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div className="input-group">
              <label>Diabetes Mellitus</label>
              <select name="dm" value={formData.dm} onChange={handleChange}>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div className="input-group">
              <label>Appetite</label>
              <select name="appet" value={formData.appet} onChange={handleChange}>
                <option value="good">Good</option>
                <option value="poor">Poor</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn-predict" disabled={loading}>
            {loading ? <Activity className="animate-spin" /> : <Send size={20} />}
            {loading ? 'Analyzing Data...' : 'Run Prediction Analysis'}
          </button>
        </form>

        {error && (
          <div className="result-card result-ckd" style={{ borderColor: '#ef4444' }}>
            <AlertTriangle size={24} style={{ marginBottom: '0.5rem' }} />
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className={`result-card ${result.prediction === 'ckd' ? 'result-ckd' : 'result-notckd'}`}>
            {result.prediction === 'ckd' ? (
              <AlertTriangle size={32} style={{ marginBottom: '1rem' }} />
            ) : (
              <CheckCircle size={32} style={{ marginBottom: '1rem' }} />
            )}
            <h2 style={{ margin: '0' }}>Result: {result.prediction.toUpperCase()}</h2>
            <p style={{ opacity: 0.8 }}>Prediction confidence is high based on the Decision Tree model.</p>
          </div>
        )}
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#64748b', fontSize: '0.875rem', display: 'flex', justifyContent: 'center', gap: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Beaker size={16} /> Fast API Engine
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ClipboardList size={16} /> Decision Tree Model
        </div>
      </div>
    </div>
  )
}

export default App
