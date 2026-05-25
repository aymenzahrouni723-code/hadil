import { useState, useEffect } from 'react';

const API_URL = '/api';

export default function Cultures() {
  const [cultures, setCultures] = useState([]);
  const [activeId, setActiveId] = useState(1);

  const fetchCultures = async () => {
    try {
      const res = await fetch(`${API_URL}/cultures`);
      const data = await res.json();
      setCultures(data.cultures);
      setActiveId(data.active_culture_id);
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  useEffect(() => { fetchCultures(); }, []);

  const activateCulture = async (id) => {
    await fetch(`${API_URL}/cultures/${id}/activate`, { method: 'POST' });
    fetchCultures();
  };

  return (
    <div className="page">
      <h2 className="page-title">🌱 Mes Cultures</h2>

      {cultures.map((culture) => (
        <div key={culture.id} className={`culture-card ${culture.id === activeId ? 'active' : ''}`}>
          <div className="culture-header">
            <div className="culture-name">
              <span className="culture-emoji">{culture.emoji}</span>
              <span className="culture-title">{culture.name}</span>
            </div>
            {culture.id === activeId && (
              <span className="culture-badge active">✅ Active</span>
            )}
          </div>

          <div className="culture-params">
            <div className="culture-param">
              <span className="culture-param-label">pH</span>
              <span className="culture-param-value">{culture.ph_min} - {culture.ph_max}</span>
            </div>
            <div className="culture-param">
              <span className="culture-param-label">EC (mS/cm)</span>
              <span className="culture-param-value">{culture.ec_min} - {culture.ec_max}</span>
            </div>
            <div className="culture-param">
              <span className="culture-param-label">Température</span>
              <span className="culture-param-value">{culture.temp_min} - {culture.temp_max}°C</span>
            </div>
            <div className="culture-param">
              <span className="culture-param-label">Humidité</span>
              <span className="culture-param-value">{culture.humidity_min} - {culture.humidity_max}%</span>
            </div>
            <div className="culture-param">
              <span className="culture-param-label">Lumière</span>
              <span className="culture-param-value">{culture.light_hours_min} - {culture.light_hours_max}h</span>
            </div>
          </div>

          <p style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-md)', lineHeight: 1.5 }}>
            {culture.description}
          </p>

          <button
            className={`culture-btn ${culture.id === activeId ? 'active-btn' : ''}`}
            onClick={() => activateCulture(culture.id)}
            disabled={culture.id === activeId}
          >
            {culture.id === activeId ? '✅ Culture Active' : 'Sélectionner'}
          </button>
        </div>
      ))}
    </div>
  );
}
