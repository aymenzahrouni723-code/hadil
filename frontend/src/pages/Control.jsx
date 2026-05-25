import { useState, useEffect } from 'react';

const API_URL = '/api';

export default function Control() {
  const [status, setStatus] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/system/status`);
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const togglePump = async () => {
    await fetch(`${API_URL}/pump/toggle`, { method: 'POST' });
    fetchStatus();
  };

  const toggleLighting = async () => {
    await fetch(`${API_URL}/lighting/toggle`, { method: 'POST' });
    fetchStatus();
  };

  const setMode = async (autoMode) => {
    await fetch(`${API_URL}/system/mode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto_mode: autoMode })
    });
    fetchStatus();
  };

  const updateThreshold = async (key, value) => {
    await fetch(`${API_URL}/settings/thresholds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [key]: parseFloat(value) })
    });
    fetchStatus();
  };

  if (!status) {
    return (
      <div className="page">
        <div className="loading"><div className="spinner"></div></div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2 className="page-title">🎛️ Contrôle Système</h2>

      {/* Mode Auto / Manuel */}
      <div className="mode-toggle">
        <button
          className={`mode-btn ${status.auto_mode ? 'active' : ''}`}
          onClick={() => setMode(true)}
        >
          🤖 Automatique
        </button>
        <button
          className={`mode-btn ${!status.auto_mode ? 'active' : ''}`}
          onClick={() => setMode(false)}
        >
          ✋ Manuel
        </button>
      </div>

      {/* Pompe à eau */}
      <div className="toggle-card">
        <div className="toggle-info">
          <div className="toggle-icon">💧</div>
          <div>
            <div className="toggle-label">Pompe à eau (600L/H)</div>
            <div className="toggle-subtitle">
              Mode: {status.auto_mode ? 'Automatique' : 'Manuel'}
            </div>
          </div>
        </div>
        <div
          className={`toggle-switch ${status.pump_on ? 'active' : ''}`}
          onClick={togglePump}
        >
          <div className="toggle-knob"></div>
        </div>
      </div>

      {/* Éclairage LED */}
      <div className="toggle-card">
        <div className="toggle-info">
          <div className="toggle-icon">💡</div>
          <div>
            <div className="toggle-label">Éclairage LED</div>
            <div className="toggle-subtitle">
              Mode: {status.auto_mode ? 'Automatique' : 'Manuel'}
            </div>
          </div>
        </div>
        <div
          className={`toggle-switch ${status.lighting_on ? 'active' : ''}`}
          onClick={toggleLighting}
        >
          <div className="toggle-knob"></div>
        </div>
      </div>

      {/* Consignes / Seuils */}
      <div className="slider-section">
        <h3>📐 Consignes</h3>

        <div className="slider-group">
          <div className="slider-label">
            <span>Seuil pH min</span>
            <span className="slider-value">{status.thresholds.ph_min}</span>
          </div>
          <input
            type="range" min="4" max="7" step="0.1"
            value={status.thresholds.ph_min}
            onChange={(e) => updateThreshold('ph_min', e.target.value)}
          />
        </div>

        <div className="slider-group">
          <div className="slider-label">
            <span>Seuil pH max</span>
            <span className="slider-value">{status.thresholds.ph_max}</span>
          </div>
          <input
            type="range" min="5" max="9" step="0.1"
            value={status.thresholds.ph_max}
            onChange={(e) => updateThreshold('ph_max', e.target.value)}
          />
        </div>

        <div className="slider-group">
          <div className="slider-label">
            <span>Seuil EC min (mS/cm)</span>
            <span className="slider-value">{status.thresholds.ec_min}</span>
          </div>
          <input
            type="range" min="0.2" max="3" step="0.1"
            value={status.thresholds.ec_min}
            onChange={(e) => updateThreshold('ec_min', e.target.value)}
          />
        </div>

        <div className="slider-group">
          <div className="slider-label">
            <span>Seuil EC max (mS/cm)</span>
            <span className="slider-value">{status.thresholds.ec_max}</span>
          </div>
          <input
            type="range" min="1" max="5" step="0.1"
            value={status.thresholds.ec_max}
            onChange={(e) => updateThreshold('ec_max', e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
