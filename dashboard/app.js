const { useState, useEffect } = React;

const API_BASE = '';

function SystemHealthDashboard() {
  const [metrics, setMetrics] = useState(null);

  const fetchData = async () => {
    const status = await fetch(`${API_BASE}/system/status`).then(r => r.json());
    let stability = {};
    try {
      stability = await fetch(`${API_BASE}/system/stability`).then(r => r.json());
    } catch (e) {
      console.error(e);
    }
    setMetrics({ ...status, ...stability });
  };

  useEffect(() => { fetchData(); }, []);

  if (!metrics) return React.createElement('p', null, 'Loading...');

  return (
    <div className="section">
      <h2>System Health</h2>
      <ul>
        <li>Active Geoids: {metrics.active_geoids}</li>
        <li>Vault A Scars: {metrics.vault_a_scars}</li>
        <li>Vault B Scars: {metrics.vault_b_scars}</li>
        <li>Cycle Count: {metrics.cycle_count}</li>
        <li>System Entropy: {metrics.system_entropy?.toFixed?.(3)}</li>
        {metrics.vault_pressure !== undefined && (
          <>
            <li>Vault Pressure: {metrics.vault_pressure.toFixed(2)}</li>
            <li>Semantic Cohesion: {metrics.semantic_cohesion.toFixed(2)}</li>
            <li>Entropic Stability: {metrics.entropic_stability.toFixed(2)}</li>
          </>
        )}
      </ul>
    </div>
  );
}

function GeoidExplorer() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const search = async () => {
    const r = await fetch(`${API_BASE}/geoids/search?query=${encodeURIComponent(query)}`).then(r => r.json());
    setResults(r.similar_geoids || []);
  };

  const trigger = async (gid) => {
    await fetch(`${API_BASE}/process/contradictions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger_geoid_id: gid, search_limit: 5 })
    });
    alert('Contradiction analysis complete');
  };

  return (
    <div className="section">
      <h2>Geoid Explorer</h2>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search geoids" />
      <button onClick={search}>Search</button>
      <ul>
        {results.map(g => (
          <li key={g.geoid_id}>
            {g.geoid_id}
            {g.metadata?.image_uri && (
              <img src={`${API_BASE}${g.metadata.image_uri}`} alt={g.geoid_id} style={{maxWidth: '100px', display: 'block'}} />
            )}
            <button onClick={() => trigger(g.geoid_id)}>Process</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function VaultInspector() {
  const [vaultA, setA] = useState([]);
  const [vaultB, setB] = useState([]);

  const fetchVaults = async () => {
    const a = await fetch(`${API_BASE}/vaults/vault_a`).then(r => r.json());
    const b = await fetch(`${API_BASE}/vaults/vault_b`).then(r => r.json());
    setA(a.scars || []);
    setB(b.scars || []);
  };

  useEffect(() => { fetchVaults(); }, []);

  return (
    <div className="section">
      <h2>Vault Inspector</h2>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div>
          <h3>Vault A</h3>
          <ul>{vaultA.map(s => <li key={s.scar_id}>{s.scar_id}</li>)}</ul>
        </div>
        <div>
          <h3>Vault B</h3>
          <ul>{vaultB.map(s => <li key={s.scar_id}>{s.scar_id}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <div>
      <h1>KIMERA SWM Dashboard</h1>
      <SystemHealthDashboard />
      <GeoidExplorer />
      <VaultInspector />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
