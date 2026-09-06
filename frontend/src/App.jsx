import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Atom,
  Boxes,
  CheckCircle2,
  Cloud,
  Cpu,
  Database,
  Gauge,
  GitBranch,
  History,
  Network,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Target,
  UploadCloud,
  Workflow,
  Zap,
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const emptyHistory = {
  total: 0,
  anomalous: 0,
  normal: 0,
  defect_rate: 0,
  items: [],
}

const demoHistory = {
  total: 128,
  anomalous: 17,
  normal: 111,
  defect_rate: 17 / 128,
  items: [
    { id: 'D-128', filename: 'bottle_012.png', predicted_label: 'anomalous', anomaly_score: 0.6415, created_at: '2026-09-06T15:42:00Z' },
    { id: 'D-127', filename: 'bottle_011.png', predicted_label: 'normal', anomaly_score: 0.1182, created_at: '2026-09-06T15:37:00Z' },
    { id: 'D-126', filename: 'bottle_010.png', predicted_label: 'normal', anomaly_score: 0.0947, created_at: '2026-09-06T15:31:00Z' },
    { id: 'D-125', filename: 'bottle_009.png', predicted_label: 'anomalous', anomaly_score: 0.5841, created_at: '2026-09-06T15:24:00Z' },
  ],
}

const emptyModelOps = {
  release_id: null,
  category: null,
  model_name: null,
  checkpoint_sha256: null,
  quality_gate_status: 'checking',
  release_image_auroc: null,
  release_pixel_auroc: null,
  mean_image_auroc: null,
  mean_pixel_auroc: null,
  experiment_tracking: 'MLflow',
  ci_cd: 'GitHub Actions + Azure DevOps',
  infrastructure_as_code: 'Bicep',
  container_registry: 'GitHub Container Registry',
  azure_target: 'Azure Static Web Apps + Container Apps + Cosmos DB',
  azure_deployment_state: 'infrastructure-ready',
}

const demoModelOps = {
  release_id: 'bottle-patchcore-v1',
  category: 'bottle',
  model_name: 'patchcore-wide_resnet50_2',
  checkpoint_sha256: '8c1e120c2554d055cf3c9d2779da2dbbd1fd8f022c632c9feab1366528d705db',
  quality_gate_status: 'pass',
  release_image_auroc: 1.0,
  release_pixel_auroc: 0.985602,
  mean_image_auroc: 0.9902182,
  mean_pixel_auroc: 0.9824854,
  experiment_tracking: 'MLflow',
  ci_cd: 'GitHub Actions + Azure DevOps',
  infrastructure_as_code: 'Bicep',
  container_registry: 'GitHub Container Registry',
  azure_target: 'Azure Static Web Apps + Container Apps + Cosmos DB',
  azure_deployment_state: 'infrastructure-ready',
}

function ScientificBackdrop() {
  return (
    <div className="science-backdrop" aria-hidden="true">
      <div className="grid-plane" />
      <div className="glow glow-a" />
      <div className="glow glow-b" />
      <div className="particle particle-1" />
      <div className="particle particle-2" />
      <div className="particle particle-3" />
      <div className="particle particle-4" />
      <div className="particle particle-5" />
      <div className="data-line data-line-a" />
      <div className="data-line data-line-b" />
    </div>
  )
}

function MetricCard({ icon: Icon, label, value, caption, accent = false }) {
  return (
    <article className={`metric-card ${accent ? 'metric-card-accent' : ''}`}>
      <div className="metric-icon"><Icon size={19} /></div>
      <div className="metric-copy">
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{caption}</small>
      </div>
      <span className="metric-pulse" />
    </article>
  )
}

export default function App() {
  const [health, setHealth] = useState(DEMO_MODE ? { status: 'demo', model_ready: true } : { status: 'checking', model_ready: false })
  const [history, setHistory] = useState(DEMO_MODE ? demoHistory : emptyHistory)
  const [modelOps, setModelOps] = useState(DEMO_MODE ? demoModelOps : emptyModelOps)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadHistory() {
    if (DEMO_MODE) return
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/inspections?limit=8`)
      if (!response.ok) return
      setHistory(await response.json())
    } catch {
      // Health status handles API availability.
    }
  }

  async function loadModelOps() {
    if (DEMO_MODE) return
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/model-ops`)
      if (!response.ok) return
      setModelOps(await response.json())
    } catch {
      setModelOps((current) => ({ ...current, quality_gate_status: 'unavailable' }))
    }
  }

  useEffect(() => {
    if (DEMO_MODE) return undefined
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
    loadModelOps()
    return () => { active = false }
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

  const releaseGate = modelOps.quality_gate_status === 'pass' ? 'Passed' : modelOps.quality_gate_status

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

    if (DEMO_MODE) {
      await new Promise((resolve) => setTimeout(resolve, 900))
      const demoResult = {
        inspection_id: 'D-129',
        filename: file.name,
        predicted_label: 'anomalous',
        anomaly_score: 0.64147,
        threshold: 0.5,
        model_name: 'patchcore-wide_resnet50_2',
        localization_base64: null,
      }
      setResult(demoResult)
      setHistory((current) => ({
        total: current.total + 1,
        anomalous: current.anomalous + 1,
        normal: current.normal,
        defect_rate: (current.anomalous + 1) / (current.total + 1),
        items: [
          { id: demoResult.inspection_id, filename: file.name, predicted_label: 'anomalous', anomaly_score: demoResult.anomaly_score, created_at: new Date().toISOString() },
          ...current.items,
        ].slice(0, 8),
      }))
      setLoading(false)
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch(`${API_BASE_URL}/api/v1/inspect`, { method: 'POST', body: formData })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'Inspection failed')
      setResult(payload)
      await loadHistory()
    } catch (requestError) {
      setError(requestError.message || 'Inspection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-root">
      <ScientificBackdrop />

      <div className="app-shell">
        <nav className="topbar">
          <div className="brand-lockup">
            <div className="brand-mark"><ScanSearch size={20} /></div>
            <div><strong>FactoryVision</strong><span>AI QUALITY SYSTEM</span></div>
          </div>
          <div className="nav-status">
            <span className="live-dot" />
            {DEMO_MODE ? 'PREVIEW NODE ONLINE' : health.model_ready ? 'MODEL RUNTIME ONLINE' : 'RUNTIME CHECK'}
          </div>
        </nav>

        {DEMO_MODE && (
          <div className="demo-banner">
            <Sparkles size={16} />
            <strong>Interactive portfolio preview</strong>
            <span>UI interactions are simulated. Model metrics are real benchmark results.</span>
          </div>
        )}

        <header className="hero-grid">
          <div className="hero-copy">
            <div className="eyebrow"><span /> INDUSTRIAL VISUAL INTELLIGENCE</div>
            <h1>See defects.<br /><em>Understand quality.</em></h1>
            <p>
              AI-powered anomaly detection and defect localization with a production-style MLOps layer built for modern manufacturing workflows.
            </p>
            <div className="hero-actions">
              <a className="primary-cta" href="#inspection"><Zap size={17} /> Launch inspection</a>
              <a className="secondary-cta" href="#mlops"><Workflow size={17} /> Explore MLOps</a>
            </div>
            <div className="hero-tech-row">
              <span>PATCHCORE</span><i />
              <span>FASTAPI</span><i />
              <span>REACT</span><i />
              <span>MLFLOW</span><i />
              <span>AZURE</span>
            </div>
          </div>

          <div className="science-visual">
            <div className="visual-label visual-label-top"><Cpu size={14} /> MODEL CORE</div>
            <div className="orbit orbit-1"><span /></div>
            <div className="orbit orbit-2"><span /></div>
            <div className="orbit orbit-3"><span /></div>
            <div className="core-ring core-ring-outer" />
            <div className="core-ring core-ring-inner" />
            <div className="core-node"><Atom size={52} /></div>
            <div className="science-crosshair science-crosshair-x" />
            <div className="science-crosshair science-crosshair-y" />
            <div className="floating-chip chip-a"><Target size={15} /><span>99.02%<small>Mean image AUROC</small></span></div>
            <div className="floating-chip chip-b"><Gauge size={15} /><span>0.6415<small>Anomaly signal</small></span></div>
            <div className="floating-chip chip-c"><ShieldCheck size={15} /><span>PASS<small>Release gate</small></span></div>
            <div className="visual-label visual-label-bottom"><Network size={14} /> SCIENTIFIC INFERENCE GRAPH</div>
          </div>
        </header>

        <section className="metrics-grid">
          <MetricCard icon={Boxes} label="Inspections" value={history.total || '—'} caption="Persisted quality samples" />
          <MetricCard icon={AlertTriangle} label="Defect rate" value={defectRate} caption="Current anomaly ratio" />
          <MetricCard icon={Activity} label="Model runtime" value={health.model_ready ? 'READY' : 'OFFLINE'} caption="PatchCore inference node" accent />
          <MetricCard icon={ShieldCheck} label="Release gate" value={releaseGate || '—'} caption="Deterministic promotion gate" />
        </section>

        <section className="pipeline-ribbon" aria-label="Inference pipeline">
          <div><UploadCloud size={16} /><span>Image ingestion</span></div><b />
          <div><Cpu size={16} /><span>PatchCore</span></div><b />
          <div><Target size={16} /><span>Localization</span></div><b />
          <div><Database size={16} /><span>Evidence store</span></div><b />
          <div><Workflow size={16} /><span>MLOps gate</span></div>
        </section>

        <section className="inspection-grid" id="inspection">
          <article className="glass-panel inspection-panel">
            <div className="panel-head">
              <div><span className="section-code">01 / INSPECTION</span><h2>Visual inspection chamber</h2></div>
              <div className="panel-icon"><ScanSearch size={23} /></div>
            </div>

            <label className={`upload-chamber ${previewUrl ? 'has-preview' : ''}`}>
              <input type="file" accept="image/*" onChange={handleFileChange} />
              {previewUrl ? (
                <div className="preview-stage">
                  <img src={previewUrl} alt="Selected inspection" />
                  <div className={`scan-beam ${loading ? 'scan-active' : ''}`} />
                  <div className="corner corner-tl" /><div className="corner corner-tr" />
                  <div className="corner corner-bl" /><div className="corner corner-br" />
                  <div className="preview-label">INPUT FRAME · {file?.name}</div>
                </div>
              ) : (
                <div className="upload-empty">
                  <div className="upload-orbit"><UploadCloud size={34} /></div>
                  <strong>Drop a product image into the vision chamber</strong>
                  <span>PNG · JPG · JPEG · maximum 6 MB</span>
                  <small>The interface will visualize inspection signals in real time.</small>
                </div>
              )}
            </label>

            <button className="inspect-button" onClick={inspectImage} disabled={!file || !health.model_ready || loading}>
              <span>{loading ? 'ANALYZING FRAME' : DEMO_MODE ? 'RUN DEMO INSPECTION' : 'RUN INSPECTION'}</span>
              <Zap size={18} />
            </button>
            {DEMO_MODE && <p className="microcopy">Preview compute is simulated so you can test the interface without cloud resources.</p>}
            {!health.model_ready && <p className="microcopy">Configure the trained checkpoint to enable live inference.</p>}
            {error && <div className="error-box">{error}</div>}
          </article>

          <article className="glass-panel result-panel">
            <div className="panel-head">
              <div><span className="section-code">02 / ANALYSIS</span><h2>Defect intelligence</h2></div>
              <div className="panel-icon"><Activity size={23} /></div>
            </div>

            {!result ? (
              <div className="idle-analysis">
                <div className="radar">
                  <span className="radar-ring radar-ring-1" />
                  <span className="radar-ring radar-ring-2" />
                  <span className="radar-ring radar-ring-3" />
                  <span className="radar-sweep" />
                  <Target size={28} />
                </div>
                <h3>Awaiting inspection signal</h3>
                <p>Run an image through the chamber to reveal anomaly probability, model confidence and localization evidence.</p>
              </div>
            ) : (
              <div className="analysis-result">
                <div className="result-topline">
                  <div className={`result-state ${result.predicted_label === 'anomalous' ? 'state-anomalous' : 'state-normal'}`}>
                    {result.predicted_label === 'anomalous' ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
                    {result.predicted_label.toUpperCase()}
                  </div>
                  <span>Inspection #{result.inspection_id}</span>
                </div>

                <div className="score-console">
                  <div><span>ANOMALY SCORE</span><strong>{Number(result.anomaly_score).toFixed(4)}</strong></div>
                  <div className="score-scale"><span style={{ width: `${Math.min(Math.max(Number(result.anomaly_score) * 100, 0), 100)}%` }} /></div>
                  <div className="scale-labels"><span>0.00 NORMAL</span><span>1.00 CRITICAL</span></div>
                </div>

                {(result.localization_base64 || (DEMO_MODE && previewUrl)) && (
                  <div className="localization-console">
                    <div className="localization-title"><Target size={15} /> DEFECT LOCALIZATION</div>
                    <div className="localization-frame">
                      {result.localization_base64 ? (
                        <img src={`data:image/png;base64,${result.localization_base64}`} alt="PatchCore anomaly localization" />
                      ) : (
                        <>
                          <img src={previewUrl} alt="Demo localization preview" />
                          <span className="thermal-zone thermal-zone-a" />
                          <span className="thermal-zone thermal-zone-b" />
                          <span className="target-reticle" />
                        </>
                      )}
                    </div>
                  </div>
                )}

                <div className="result-metadata">
                  <div><span>MODEL</span><strong>{result.model_name}</strong></div>
                  <div><span>THRESHOLD</span><strong>{Number(result.threshold).toFixed(2)}</strong></div>
                  <div><span>FILE</span><strong>{result.filename}</strong></div>
                </div>
              </div>
            )}
          </article>
        </section>

        <section className="glass-panel mlops-section" id="mlops">
          <div className="panel-head mlops-head">
            <div><span className="section-code">03 / MODEL OPERATIONS</span><h2>Release intelligence & MLOps graph</h2></div>
            <div className="mlops-state"><span /> AZURE-ORIENTED PIPELINE READY</div>
          </div>

          <div className="mlops-layout">
            <div className="release-console">
              <div className="release-heading">
                <div className={`gate-badge ${modelOps.quality_gate_status === 'pass' ? 'gate-pass' : ''}`}><ShieldCheck size={16} /> QUALITY GATE · {String(modelOps.quality_gate_status).toUpperCase()}</div>
                <h3>{modelOps.release_id || 'Release metadata unavailable'}</h3>
                <p>{modelOps.model_name || 'PatchCore'} · category: {modelOps.category || 'pending'}</p>
              </div>

              <div className="metric-bars">
                {[
                  ['Release image AUROC', modelOps.release_image_auroc],
                  ['Release pixel AUROC', modelOps.release_pixel_auroc],
                  ['Mean image AUROC', modelOps.mean_image_auroc],
                  ['Mean pixel AUROC', modelOps.mean_pixel_auroc],
                ].map(([label, value]) => (
                  <div className="metric-bar" key={label}>
                    <div><span>{label}</span><strong>{value != null ? Number(value).toFixed(4) : '—'}</strong></div>
                    <div className="bar-track"><span style={{ width: value != null ? `${Math.min(Number(value) * 100, 100)}%` : '0%' }} /></div>
                  </div>
                ))}
              </div>
            </div>

            <div className="ops-graph">
              <div className="ops-node"><GitBranch size={18} /><span><strong>CI/CD</strong>{modelOps.ci_cd}</span></div>
              <div className="ops-link" />
              <div className="ops-node"><Activity size={18} /><span><strong>Experiments</strong>{modelOps.experiment_tracking}</span></div>
              <div className="ops-link" />
              <div className="ops-node"><Boxes size={18} /><span><strong>Registry</strong>{modelOps.container_registry}</span></div>
              <div className="ops-link" />
              <div className="ops-node ops-node-azure"><Cloud size={18} /><span><strong>Azure target</strong>{modelOps.azure_target}</span></div>
            </div>
          </div>
        </section>

        <section className="glass-panel history-section">
          <div className="panel-head">
            <div><span className="section-code">04 / QUALITY MEMORY</span><h2>Inspection timeline</h2></div>
            <div className="panel-icon"><History size={23} /></div>
          </div>

          {!history.items.length ? <p className="empty-history">No persisted inspections yet.</p> : (
            <div className="timeline-table-wrap">
              <table className="timeline-table">
                <thead><tr><th>Inspection</th><th>Frame</th><th>Classification</th><th>Signal</th><th>Timestamp</th></tr></thead>
                <tbody>
                  {history.items.map((item) => (
                    <tr key={item.id}>
                      <td><span className="id-chip">#{item.id}</span></td>
                      <td>{item.filename}</td>
                      <td><span className={`classification ${item.predicted_label === 'anomalous' ? 'classification-danger' : 'classification-ok'}`}>{item.predicted_label}</span></td>
                      <td><strong>{Number(item.anomaly_score).toFixed(4)}</strong></td>
                      <td>{new Date(item.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer className="footer-bar">
          <div><span className="footer-mark"><ScanSearch size={16} /></span> FactoryVision AI · Industrial Computer Vision & MLOps</div>
          <div>PATCHCORE · FASTAPI · REACT · MLFLOW · AZURE DEVOPS · BICEP</div>
        </footer>
      </div>
    </div>
  )
}
