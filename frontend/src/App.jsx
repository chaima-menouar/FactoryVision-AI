import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Box,
  Boxes,
  Cable,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Cloud,
  Cpu,
  Database,
  Gauge,
  GitBranch,
  Hexagon,
  Layers,
  Network,
  Package,
  Play,
  ScanLine,
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

const demoHistory = {
  total: 128,
  anomalous: 17,
  normal: 111,
  defect_rate: 17 / 128,
  items: [
    { id: 'D-128', filename: 'bottle_012.png', predicted_label: 'anomalous', anomaly_score: 0.6415, created_at: '2026-09-06T15:42:00Z' },
    { id: 'D-127', filename: 'zipper_021.png', predicted_label: 'normal', anomaly_score: 0.1182, created_at: '2026-09-06T15:37:00Z' },
    { id: 'D-126', filename: 'metal_nut_008.png', predicted_label: 'normal', anomaly_score: 0.0947, created_at: '2026-09-06T15:31:00Z' },
    { id: 'D-125', filename: 'transistor_014.png', predicted_label: 'anomalous', anomaly_score: 0.5841, created_at: '2026-09-06T15:24:00Z' },
  ],
}

const emptyHistory = { total: 0, anomalous: 0, normal: 0, defect_rate: 0, items: [] }

const realMetrics = {
  release_id: 'bottle-patchcore-v1',
  category: 'bottle',
  model_name: 'patchcore-wide_resnet50_2',
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

const products = [
  { key: 'bottle', label: 'Bottle', defect: 'Crack / deformation', score: '1.0000 AUROC' },
  { key: 'zipper', label: 'Zipper', defect: 'Missing teeth', score: '0.9753 AUROC' },
  { key: 'nut', label: 'Metal nut', defect: 'Scratch / deformation', score: '0.9971 AUROC' },
  { key: 'transistor', label: 'Transistor', defect: 'Surface anomaly', score: '0.9958 AUROC' },
  { key: 'cable', label: 'Cable', defect: 'Cut / exposed wire', score: '0.9829 AUROC' },
]

function ProductGlyph({ type = 'bottle', className = '' }) {
  if (type === 'zipper') {
    return (
      <svg className={className} viewBox="0 0 120 120" aria-hidden="true">
        <path d="M34 12v96M86 12v96" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        {Array.from({ length: 7 }).map((_, index) => (
          <g key={index} transform={`translate(0 ${index * 14})`}>
            <rect x="34" y="14" width="22" height="9" rx="3" fill="currentColor" />
            <rect x="64" y="21" width="22" height="9" rx="3" fill="currentColor" />
          </g>
        ))}
      </svg>
    )
  }

  if (type === 'nut') {
    return (
      <svg className={className} viewBox="0 0 120 120" aria-hidden="true">
        <path d="M60 12 101 36v48l-41 24L19 84V36Z" fill="none" stroke="currentColor" strokeWidth="9" strokeLinejoin="round" />
        <circle cx="60" cy="60" r="19" fill="none" stroke="currentColor" strokeWidth="9" />
      </svg>
    )
  }

  if (type === 'transistor') {
    return (
      <svg className={className} viewBox="0 0 120 120" aria-hidden="true">
        <rect x="28" y="28" width="64" height="64" rx="13" fill="none" stroke="currentColor" strokeWidth="8" />
        <rect x="43" y="43" width="34" height="34" rx="8" fill="currentColor" opacity=".28" />
        {[22, 42, 62, 82].map((value) => (
          <g key={value}>
            <path d={`M${value} 12v16M${value} 92v16`} stroke="currentColor" strokeWidth="6" strokeLinecap="round" />
            <path d={`M12 ${value}h16M92 ${value}h16`} stroke="currentColor" strokeWidth="6" strokeLinecap="round" />
          </g>
        ))}
      </svg>
    )
  }

  if (type === 'cable') {
    return (
      <svg className={className} viewBox="0 0 120 120" aria-hidden="true">
        <path d="M12 82c18-54 38-55 53-25s25 29 43-14" fill="none" stroke="currentColor" strokeWidth="12" strokeLinecap="round" />
        <path d="M99 35 111 23M103 42l15-5" stroke="currentColor" strokeWidth="5" strokeLinecap="round" />
        <circle cx="66" cy="61" r="11" fill="none" stroke="currentColor" strokeWidth="4" opacity=".45" />
      </svg>
    )
  }

  return (
    <svg className={className} viewBox="0 0 120 120" aria-hidden="true">
      <path d="M48 13h24v15l8 9v15c0 8 13 12 13 27v17c0 8-7 14-15 14H42c-8 0-15-6-15-14V79c0-15 13-19 13-27V37l8-9Z" fill="none" stroke="currentColor" strokeWidth="8" strokeLinejoin="round" />
      <path d="M43 58h34" stroke="currentColor" strokeWidth="5" strokeLinecap="round" opacity=".45" />
    </svg>
  )
}

function AnimatedBackground() {
  return (
    <div className="fv-bg" aria-hidden="true">
      <div className="fv-grid" />
      <div className="fv-aurora fv-aurora-a" />
      <div className="fv-aurora fv-aurora-b" />
      <div className="fv-aurora fv-aurora-c" />
      {Array.from({ length: 22 }).map((_, index) => (
        <i key={index} className={`fv-star fv-star-${(index % 8) + 1}`} style={{ '--delay': `${-(index * 0.43)}s`, '--x': `${(index * 47) % 97}%`, '--y': `${(index * 31) % 94}%` }} />
      ))}
      <div className="fv-beam fv-beam-a" />
      <div className="fv-beam fv-beam-b" />
    </div>
  )
}

function StatCard({ icon: Icon, value, label, caption, tone = 'cyan' }) {
  return (
    <article className={`fv-stat fv-tone-${tone}`}>
      <div className="fv-stat-icon"><Icon size={19} /></div>
      <div>
        <strong>{value}</strong>
        <span>{label}</span>
        <small>{caption}</small>
      </div>
      <i className="fv-stat-glow" />
    </article>
  )
}

function ScannerVisual() {
  return (
    <div className="fv-scanner-scene" aria-label="Animated AI inspection scanner illustration">
      <div className="fv-machine">
        <div className="fv-machine-top"><ScanSearch size={23} /><span>FACTORYVISION AI</span></div>
        <div className="fv-lens"><span /><span /><i /></div>
        <div className="fv-scan-cone" />
      </div>

      <div className="fv-holo-volume">
        <div className="fv-holo-box">
          <ProductGlyph type="bottle" className="fv-hero-product" />
          <span className="fv-defect-heat" />
          <span className="fv-reticle" />
        </div>
      </div>

      <div className="fv-conveyor">
        <div className="fv-belt">
          {['bottle', 'bottle', 'bottle', 'bottle', 'bottle', 'bottle'].map((type, index) => (
            <div className="fv-belt-product" key={`${type}-${index}`}><ProductGlyph type={type} /></div>
          ))}
        </div>
      </div>

      <div className="fv-detect-card">
        <div className="fv-card-head"><span className="fv-live-dot" /> LIVE DETECTION</div>
        <div className="fv-card-product"><ProductGlyph type="bottle" /><div><strong>Bottle</strong><span>Crack anomaly</span></div></div>
        <div className="fv-card-confidence"><span>CONFIDENCE SIGNAL</span><strong>0.6415</strong></div>
        <div className="fv-card-bar"><i /></div>
      </div>

      <div className="fv-orbit-ring fv-orbit-1"><i /></div>
      <div className="fv-orbit-ring fv-orbit-2"><i /></div>
      <div className="fv-hero-badge fv-badge-a"><CircleDot size={14} /><span>PATCHCORE<small>Wide ResNet50</small></span></div>
      <div className="fv-hero-badge fv-badge-b"><ShieldCheck size={14} /><span>PASS<small>Release gate</small></span></div>
    </div>
  )
}

function ProductRail({ selected, onSelect }) {
  return (
    <aside className="fv-product-rail">
      <div className="fv-rail-title"><Sparkles size={14} /> INSPECTION TARGETS</div>
      {products.map((product) => (
        <button
          type="button"
          className={`fv-product-chip ${selected === product.key ? 'is-selected' : ''}`}
          onClick={() => onSelect(product.key)}
          key={product.key}
        >
          <div className="fv-product-thumb">
            <ProductGlyph type={product.key} />
            <span className={`fv-mini-heat heat-${product.key}`} />
          </div>
          <span><strong>{product.label}</strong><small>{product.defect}</small></span>
          <ChevronRight size={16} />
        </button>
      ))}
    </aside>
  )
}

export default function App() {
  const [health, setHealth] = useState(DEMO_MODE ? { status: 'demo', model_ready: true } : { status: 'checking', model_ready: false })
  const [history, setHistory] = useState(DEMO_MODE ? demoHistory : emptyHistory)
  const [modelOps, setModelOps] = useState(DEMO_MODE ? realMetrics : realMetrics)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [selectedProduct, setSelectedProduct] = useState('bottle')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadHistory() {
    if (DEMO_MODE) return
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/inspections?limit=8`)
      if (response.ok) setHistory(await response.json())
    } catch {
      // Health state covers API availability.
    }
  }

  async function loadModelOps() {
    if (DEMO_MODE) return
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/model-ops`)
      if (response.ok) setModelOps(await response.json())
    } catch {
      // Keep benchmark metadata visible if the optional endpoint is unavailable.
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
      .then((payload) => { if (active) setHealth(payload) })
      .catch(() => { if (active) setHealth({ status: 'offline', model_ready: false }) })
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

  const defectRate = useMemo(() => history.total ? `${(history.defect_rate * 100).toFixed(1)}%` : '—', [history])

  function chooseProduct(key) {
    setSelectedProduct(key)
    setFile(null)
    setResult(null)
    setError('')
  }

  function handleFileChange(event) {
    const selected = event.target.files?.[0]
    if (!selected) return
    setFile(selected)
    setResult(null)
    setError('')
  }

  async function inspectImage() {
    if (!health.model_ready) return
    setLoading(true)
    setError('')

    if (DEMO_MODE) {
      await new Promise((resolve) => setTimeout(resolve, 1400))
      const product = products.find((item) => item.key === selectedProduct) || products[0]
      const demoResult = {
        inspection_id: `D-${129 + history.total - 128}`,
        filename: file?.name || `${selectedProduct}_demo_sample.png`,
        predicted_label: 'anomalous',
        anomaly_score: selectedProduct === 'bottle' ? 0.64147 : selectedProduct === 'nut' ? 0.5841 : 0.6178,
        threshold: 0.5,
        model_name: 'patchcore-wide_resnet50_2',
        defect_type: product.defect,
        localization_base64: null,
      }
      setResult(demoResult)
      setHistory((current) => ({
        total: current.total + 1,
        anomalous: current.anomalous + 1,
        normal: current.normal,
        defect_rate: (current.anomalous + 1) / (current.total + 1),
        items: [
          { id: demoResult.inspection_id, filename: demoResult.filename, predicted_label: demoResult.predicted_label, anomaly_score: demoResult.anomaly_score, created_at: new Date().toISOString() },
          ...current.items,
        ].slice(0, 6),
      }))
      setLoading(false)
      return
    }

    if (!file) {
      setError('Select an image before running live inspection.')
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
    <div className="fv-app">
      <AnimatedBackground />

      <header className="fv-nav">
        <a className="fv-brand" href="#top">
          <span className="fv-brand-mark"><ScanSearch size={21} /></span>
          <span><strong>FactoryVision</strong><b>AI</b><small>INDUSTRIAL INTELLIGENCE</small></span>
        </a>
        <nav className="fv-nav-links">
          <a href="#inspection">Inspection</a>
          <a href="#products">Products</a>
          <a href="#mlops">MLOps</a>
          <a href="#history">Analytics</a>
        </nav>
        <a className="fv-nav-cta" href="#inspection">Try demo <ChevronRight size={15} /></a>
      </header>

      <main id="top" className="fv-shell">
        {DEMO_MODE && (
          <div className="fv-preview-note"><Sparkles size={14} /><strong>Interactive portfolio preview</strong><span>Interaction is simulated; benchmark metrics are real.</span></div>
        )}

        <section className="fv-hero">
          <div className="fv-hero-copy">
            <div className="fv-kicker"><span /> AI-POWERED MANUFACTURING QUALITY</div>
            <h1>AI sees what<br /><em>others miss.</em></h1>
            <p>Detect, localize and understand industrial defects with a production-style computer vision and MLOps workflow built around PatchCore.</p>
            <div className="fv-hero-actions">
              <a className="fv-btn fv-btn-primary" href="#inspection"><Zap size={17} /> Launch inspection <ChevronRight size={16} /></a>
              <a className="fv-btn fv-btn-ghost" href="#mlops"><Play size={16} /> Explore MLOps</a>
            </div>
            <div className="fv-tech-line">
              <span>PATCHCORE</span><i /><span>FASTAPI</span><i /><span>REACT</span><i /><span>MLFLOW</span><i /><span>AZURE READY</span>
            </div>
          </div>

          <ScannerVisual />
          <ProductRail selected={selectedProduct} onSelect={chooseProduct} />
        </section>

        <section className="fv-stats">
          <StatCard icon={Target} value="99.02%" label="Mean image AUROC" caption="Five-category benchmark" tone="cyan" />
          <StatCard icon={Gauge} value="98.25%" label="Mean pixel AUROC" caption="Localization benchmark" tone="violet" />
          <StatCard icon={ShieldCheck} value="PASS" label="Release quality gate" caption="Model promotion checks" tone="green" />
          <StatCard icon={Activity} value="5" label="MVTec categories" caption="Bottle · cable · nut · transistor · zipper" tone="pink" />
        </section>

        <section className="fv-feature-strip">
          <div><Target /><span><strong>Anomaly detection</strong><small>PatchCore scoring</small></span></div>
          <div><ScanLine /><span><strong>Defect localization</strong><small>Heatmap evidence</small></span></div>
          <div><Workflow /><span><strong>MLOps lifecycle</strong><small>MLflow + quality gates</small></span></div>
          <div><Cloud /><span><strong>Cloud-ready</strong><small>Azure-oriented architecture</small></span></div>
          <div><Database /><span><strong>Quality history</strong><small>Persisted inspections</small></span></div>
        </section>

        <section id="inspection" className="fv-workspace">
          <article className="fv-panel fv-upload-panel">
            <div className="fv-panel-head">
              <div><span>01 / VISION INPUT</span><h2>See the power of AI inspection</h2><p>Upload your own frame or choose one of the product targets.</p></div>
              <span className="fv-panel-icon"><UploadCloud /></span>
            </div>

            <label className={`fv-dropzone ${previewUrl ? 'has-image' : ''}`}>
              <input type="file" accept="image/*" onChange={handleFileChange} />
              {previewUrl ? (
                <div className="fv-image-stage">
                  <img src={previewUrl} alt="Selected inspection input" />
                  <div className={`fv-stage-scan ${loading ? 'is-scanning' : ''}`} />
                  <span className="fv-corner c1" /><span className="fv-corner c2" /><span className="fv-corner c3" /><span className="fv-corner c4" />
                  <div className="fv-stage-tag">INPUT FRAME · {file?.name}</div>
                </div>
              ) : (
                <div className="fv-empty-stage">
                  <div className="fv-product-preview">
                    <div className="fv-preview-rings"><span /><span /><span /></div>
                    <ProductGlyph type={selectedProduct} />
                    <i className="fv-preview-heat" />
                  </div>
                  <strong>{products.find((item) => item.key === selectedProduct)?.label} inspection target</strong>
                  <span>Drag & drop a product image or click to upload</span>
                  <small>PNG · JPG · JPEG · max 6 MB</small>
                </div>
              )}
            </label>

            <div id="products" className="fv-example-grid">
              {products.map((product) => (
                <button key={product.key} type="button" className={selectedProduct === product.key ? 'active' : ''} onClick={() => chooseProduct(product.key)}>
                  <ProductGlyph type={product.key} /><span>{product.label}</span>
                </button>
              ))}
            </div>

            <button type="button" className="fv-analyze-btn" disabled={!health.model_ready || loading} onClick={inspectImage}>
              <span>{loading ? 'ANALYZING VISUAL SIGNAL...' : DEMO_MODE ? 'ANALYZE WITH AI' : 'RUN LIVE INSPECTION'}</span>
              {loading ? <Activity className="fv-spin" size={18} /> : <Zap size={18} />}
            </button>
            {error && <div className="fv-error">{error}</div>}
          </article>

          <article className="fv-panel fv-result-panel">
            <div className="fv-panel-head">
              <div><span>02 / DEFECT INTELLIGENCE</span><h2>Inspection results dashboard</h2><p>Evidence, score and localization in one view.</p></div>
              <div className="fv-live-pill"><i /> REAL-TIME</div>
            </div>

            {!result ? (
              <div className="fv-awaiting">
                <div className="fv-radar">
                  <i className="r1" /><i className="r2" /><i className="r3" /><span /><Target size={34} />
                </div>
                <h3>Awaiting inspection signal</h3>
                <p>Launch an inspection to reveal anomaly probability, localization evidence and quality status.</p>
                <div className="fv-signal-bars">{Array.from({ length: 16 }).map((_, i) => <i key={i} style={{ '--h': `${18 + ((i * 17) % 60)}%`, '--d': `${i * .07}s` }} />)}</div>
              </div>
            ) : (
              <div className="fv-result-content">
                <div className="fv-result-main">
                  <div className="fv-result-visual">
                    {previewUrl ? <img src={previewUrl} alt="Analyzed input" /> : <ProductGlyph type={selectedProduct} />}
                    <span className="fv-result-heat" />
                    <span className="fv-result-target" />
                    <div className="fv-defect-label"><AlertTriangle size={13} /> DEFECT</div>
                    <div className="fv-result-scanline" />
                  </div>
                  <div className="fv-result-data">
                    <div className="fv-result-title"><div><span>PRODUCT</span><strong>{products.find((item) => item.key === selectedProduct)?.label}</strong></div><div className="fv-status-bad"><AlertTriangle size={15} /> ANOMALY DETECTED</div></div>
                    <dl>
                      <div><dt>Anomaly score</dt><dd>{Number(result.anomaly_score).toFixed(4)}</dd></div>
                      <div><dt>Threshold</dt><dd>{Number(result.threshold).toFixed(2)}</dd></div>
                      <div><dt>Defect type</dt><dd>{result.defect_type || products.find((item) => item.key === selectedProduct)?.defect}</dd></div>
                      <div><dt>Model</dt><dd>{result.model_name}</dd></div>
                    </dl>
                  </div>
                </div>

                <div className="fv-quality-chart">
                  <div className="fv-chart-head"><span><i /> PASS RATE TREND</span><strong>96.1%</strong></div>
                  <div className="fv-chart-grid"><svg viewBox="0 0 520 150" preserveAspectRatio="none"><defs><linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#27f0df" stopOpacity=".45"/><stop offset="100%" stopColor="#27f0df" stopOpacity="0"/></linearGradient></defs><path className="fv-area" d="M0 118 C42 105 58 94 92 98 S145 78 185 83 S238 70 276 73 S338 56 374 61 S432 44 520 48 L520 150 L0 150Z" fill="url(#chartGradient)"/><path className="fv-line" d="M0 118 C42 105 58 94 92 98 S145 78 185 83 S238 70 276 73 S338 56 374 61 S432 44 520 48" fill="none" stroke="currentColor" strokeWidth="3"/></svg></div>
                </div>

                <div className="fv-gauge-row">
                  <div className="fv-gauge"><div className="fv-gauge-ring"><span>{history.total}</span><small>INSPECTED</small></div></div>
                  <div className="fv-gauge-legend"><span><i className="good" /> Good <strong>{history.normal}</strong></span><span><i className="bad" /> Defect <strong>{history.anomalous}</strong></span><span><i className="info" /> Defect rate <strong>{defectRate}</strong></span></div>
                </div>
              </div>
            )}
          </article>
        </section>

        <section id="mlops" className="fv-panel fv-mlops">
          <div className="fv-panel-head">
            <div><span>03 / MODEL OPERATIONS</span><h2>MLOps command center</h2><p>From experiment evidence to versioned release and cloud-ready infrastructure.</p></div>
            <div className="fv-mlops-status"><i /> RELEASE PIPELINE READY</div>
          </div>

          <div className="fv-mlops-grid">
            <div className="fv-release-card">
              <div className="fv-release-orbit"><Network size={38} /><span /><i /></div>
              <div><span>ACTIVE MODEL RELEASE</span><h3>{modelOps.release_id || 'bottle-patchcore-v1'}</h3><p>{modelOps.model_name || 'patchcore-wide_resnet50_2'}</p></div>
              <div className="fv-gate-pass"><ShieldCheck size={16} /> QUALITY GATE PASS</div>
            </div>

            <div className="fv-pipeline-map">
              {[
                { icon: BarChart3, label: 'Experiments', sub: 'MLflow' },
                { icon: ShieldCheck, label: 'Quality gate', sub: 'Benchmark validation' },
                { icon: Box, label: 'Artifact', sub: 'SHA-256 verified' },
                { icon: GitBranch, label: 'CI/CD', sub: 'GitHub + Azure DevOps' },
                { icon: Cloud, label: 'Cloud target', sub: 'Azure architecture' },
              ].map(({ icon: Icon, label, sub }, index) => (
                <div className="fv-pipeline-node" key={label}><div><Icon size={18} /></div><span><strong>{label}</strong><small>{sub}</small></span>{index < 4 && <i className="fv-pipeline-link" />}</div>
              ))}
            </div>
          </div>

          <div className="fv-benchmark-row">
            <div><span>BOTTLE IMAGE AUROC</span><strong>1.0000</strong></div>
            <div><span>BOTTLE PIXEL AUROC</span><strong>0.9856</strong></div>
            <div><span>MEAN IMAGE AUROC</span><strong>0.9902</strong></div>
            <div><span>MEAN PIXEL AUROC</span><strong>0.9825</strong></div>
          </div>
        </section>

        <section id="history" className="fv-panel fv-history">
          <div className="fv-panel-head">
            <div><span>04 / QUALITY ANALYTICS</span><h2>Recent inspections</h2><p>A compact audit trail of recent quality decisions.</p></div>
            <span className="fv-panel-icon"><Layers /></span>
          </div>

          <div className="fv-history-table">
            <div className="fv-history-head"><span>ID</span><span>PRODUCT FRAME</span><span>RESULT</span><span>SCORE</span><span>TIME</span></div>
            {history.items.map((item) => (
              <div className="fv-history-row" key={item.id}>
                <span>#{item.id}</span>
                <span><Package size={15} /> {item.filename}</span>
                <span className={item.predicted_label === 'anomalous' ? 'is-bad' : 'is-good'}>{item.predicted_label === 'anomalous' ? <AlertTriangle size={13} /> : <CheckCircle2 size={13} />}{item.predicted_label}</span>
                <strong>{Number(item.anomaly_score).toFixed(4)}</strong>
                <span>{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            ))}
          </div>
        </section>

        <footer className="fv-footer">
          <div className="fv-brand"><span className="fv-brand-mark"><ScanSearch size={19} /></span><span><strong>FactoryVision</strong><b>AI</b></span></div>
          <p>Computer vision · anomaly detection · MLOps · cloud-ready quality intelligence</p>
          <span>Portfolio demo · v1.0</span>
        </footer>
      </main>
    </div>
  )
}
