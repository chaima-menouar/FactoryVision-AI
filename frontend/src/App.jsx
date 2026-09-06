import { Activity, AlertTriangle, Boxes, ScanSearch } from 'lucide-react'

const metrics = [
  { label: 'Inspections', value: '—', icon: Boxes },
  { label: 'Defect rate', value: '—', icon: AlertTriangle },
  { label: 'Model status', value: 'Not trained', icon: Activity },
]

export default function App() {
  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">INDUSTRIAL QUALITY INTELLIGENCE</p>
          <h1>FactoryVision AI</h1>
          <p className="subtitle">Visual defect detection, localization, analytics and an AI quality copilot.</p>
        </div>
        <div className="status">v0.1 · Foundation</div>
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
        <div className="panel upload">
          <ScanSearch size={36} />
          <h2>Inspection workspace</h2>
          <p>The UI shell is ready. Image inspection will be enabled after the hosted baseline model is trained and connected to the API.</p>
          <button disabled>Inspect image</button>
        </div>
        <div className="panel">
          <h2>Current phase</h2>
          <ol>
            <li>Dataset strategy and validation</li>
            <li>Hosted anomaly-detection baseline</li>
            <li>Evaluation and anomaly maps</li>
            <li>API + inspection history</li>
          </ol>
        </div>
      </section>
    </main>
  )
}
