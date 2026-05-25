import { useState, useEffect } from 'react';

const API_URL = '/api';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_URL}/alerts?limit=50`);
      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const acknowledgeAlert = async (id) => {
    await fetch(`${API_URL}/alerts/${id}/acknowledge`, { method: 'POST' });
    fetchAlerts();
  };

  const acknowledgeAll = async () => {
    await fetch(`${API_URL}/alerts/acknowledge-all`, { method: 'POST' });
    fetchAlerts();
  };

  const unreadCount = alerts.filter(a => !a.acknowledged).length;

  const getAlertIcon = (type, severity) => {
    if (severity === 'critical') return '⚠️';
    if (type === 'water_level') return '💧';
    if (type === 'temperature') return '🌡️';
    if (type === 'ph') return '🧪';
    if (type === 'ec') return '⚡';
    if (type === 'pump') return '🔧';
    return 'ℹ️';
  };

  const formatTime = (timestamp) => {
    const d = new Date(timestamp);
    return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <h2 className="page-title" style={{ margin: 0 }}>
          🔔 Alertes
          {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
        </h2>
        {unreadCount > 0 && (
          <button className="ack-all-btn" onClick={acknowledgeAll}>
            Tout acquitter
          </button>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✅</div>
          <p>Aucune alerte</p>
          <p style={{ fontSize: '0.8rem', marginTop: '8px' }}>Le système fonctionne normalement</p>
        </div>
      ) : (
        alerts.map((alert) => (
          <div key={alert.id} className={`alert-card ${alert.severity} ${alert.acknowledged ? 'acknowledged' : ''}`}>
            <div className="alert-card-header">
              <div className="alert-message">
                {getAlertIcon(alert.type, alert.severity)} {alert.message}
              </div>
              <span className="alert-time">{formatTime(alert.timestamp)}</span>
            </div>

            {alert.threshold && (
              <div className="alert-threshold">Seuil: {alert.threshold}</div>
            )}

            {!alert.acknowledged && (
              <button className="alert-ack-btn" onClick={() => acknowledgeAlert(alert.id)}>
                Acquitter
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
}
