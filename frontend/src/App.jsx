import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, Boxes, CheckCircle2, History, ScanSearch, UploadCloud } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const emptyHistory = {
  total: 0,
  anomalous: 0,
  normal: 0,
  defect_rate: 0,
  items: [],
}

export default function App() {
  const [health, setHealth] = useState({ status: 'checking', model_ready: false })
  const [history, setHistory] = useState(emptyHistory)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/inspections?limit=8`)
      if (!response.ok) return
      const payload = await response.json()
      setHistory(payload)
    } catch {
      // History is supplementary; health status handles API availability.
    }
  }

  useEffect(() => {
    let active = true

    fetch(`${API_BASE_URL}/health`)
      .then((response) => {
        if (!response.ok) throw new Error('API health check failed')
        return response.json()
      })
      .then((payload) => {
        if (active) setHealth(payload)
      })
      .catch(() => {
        if (active) setHealth({ status: 'offline', model_ready: false })
      })

    loadHistory()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return undefined
    }

    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const defectRate = useMemo(() => {
    if (!history.total) return '—'
    return `${(history.defect_rate * 100).toFixed(1)}%`
  }, [history])

  const metrics = [
    { label: 'Inspections', value: history.total || '—', icon: Boxes },
    { label: 'Defect rate', value: defectRate, icon: AlertTriangle },
    {
      label: 'Model status',
      value: health.model_ready ? 'PatchCore ready' : health.status === 'offline' ? 'API offline' : 'Model not ready',
      icon: Activity,
    },
  ]

  function handleFileChange(event) {
    const selected = event.target.files?.[0]
    if (!selected) return
    setFile(selected)
    setResult(null)
    setError('')
  }

  async function inspectImage() {
    if (!file || !health.model_ready) return

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/api/v1/inspect`, {
        method: 'POST',
        body: formData,
      })

      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.detail || 'Inspection failed')
      }

      setResult(payload)
      await loadHistory()
    } catch (requestError) {
      setError(requestError.message || 'Inspection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">INDUSTRIAL QUALITY INTELLIGENCE</p>
          <h1>FactoryVision AI</h1>
          <p className="subtitle">Visual defect detection, localization, analytics and an AI quality copilot.</p>
        </div>
        <div className={`status ${health.model_ready ? 'status-ready' : ''}`}>
          <span className="status-dot" />
          v0.6 · Inspection intelligence
        </div>
      </header>

      <section className="metrics">
        {metrics.map(({ label, value, icon: Icon }) => (
          <article className="card" key={label}>
            <Icon size={20} />
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="workspace">
        <div className="panel inspection-panel">
          <div className="panel-heading">
            <div>
              <p className="section-kicker">LIVE INSPECTION</p>
              <h2>Inspection workspace</h2>
            </div>
            <ScanSearch size={32} />
          </div>

          <label className="dropzone">
            <input type="file" accept="image/*" onChange={handleFileChange} />
            {previewUrl ? (
              <img className="preview" src={previewUrl} alt="Selected inspection" />
            ) : (
              <div className="dropzone-empty">
                <UploadCloud size={34} />
                <strong>Select a product image</strong>
                <span>PNG, JPG or JPEG</span>
              </div>
            )}
          </label>

          <button
            className="primary-button"
            onClick={inspectImage}
            disabled={!file || !health.model_ready || loading}
          >
            {loading ? 'Inspecting…' : 'Inspect image'}
          </button>

          {!health.model_ready && (
            <p className="hint">Configure the trained checkpoint on the backend to enable live inference.</p>
          )}

          {error && <div className="message error-message">{error}</div>}
        </div>

        <div className="panel result-panel">
          <p className="section-kicker">MODEL OUTPUT</p>
          <h2>Inspection result</h2>

          {!result ? (
            <div className="empty-result">
              <Activity size={30} />
              <p>Run an inspection to see the PatchCore prediction, anomaly score and defect localization.</p>
            </div>
          ) : (
            <div className="result-content">
              <div className={`result-badge ${result.predicted_label === 'anomalous' ? 'result-defect' : 'result-normal'}`}>
                {result.predicted_label === 'anomalous' ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
                {result.predicted_label}
              </div>

              <div className="score-block">
                <span>Anomaly score</span>
                <strong>{Number(result.anomaly_score).toFixed(4)}</strong>
                <div className="score-track">
                  <div
                    className="score-fill"
                    style={{ width: `${Math.min(Math.max(Number(result.anomaly_score) * 100, 0), 100)}%` }}
                  />
                </div>
              </div>

              {result.localization_base64 && (
                <div className="localization-block">
                  <span>Defect localization</span>
                  <img
                    src={`data:image/png;base64,${result.localization_base64}`}
                    alt="PatchCore anomaly localization"
                  />
                </div>
              )}

              <dl className="result-details">
                <div><dt>Inspection</dt><dd>{result.inspection_id ? `#${result.inspection_id}` : '—'}</dd></div>
                <div><dt>File</dt><dd>{result.filename}</dd></div>
                <div><dt>Threshold</dt><dd>{Number(result.threshold).toFixed(2)}</dd></div>
                <div><dt>Model</dt><dd>{result.model_name}</dd></div>
              </dl>
            </div>
          )}
        </div>
      </section>

      <section className="panel history-panel">
        <div className="panel-heading">
          <div>
            <p className="section-kicker">QUALITY HISTORY</p>
            <h2>Recent inspections</h2>
          </div>
          <History size={28} />
        </div>

        {!history.items.length ? (
          <p className="history-empty">No persisted inspections yet.</p>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>File</th>
                  <th>Result</th>
                  <th>Score</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {history.items.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>{item.filename}</td>
                    <td>
                      <span className={`history-label ${item.predicted_label === 'anomalous' ? 'history-defect' : 'history-normal'}`}>
                        {item.predicted_label}
                      </span>
                    </td>
                    <td>{Number(item.anomaly_score).toFixed(4)}</td>
                    <td>{new Date(item.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}
