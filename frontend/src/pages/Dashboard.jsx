import { useState, useEffect } from 'react';
import GaugeCard from '../components/GaugeCard';

const API_URL = '/api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [latestAlert, setLatestAlert] = useState(null);

  const fetchData = async () => {
    try {
      const [sensorsRes, alertsRes] = await Promise.all([
        fetch(`${API_URL}/sensors/current`),
        fetch(`${API_URL}/alerts?limit=1`)
      ]);
      const sensorsData = await sensorsRes.json();
      const alertsData = await alertsRes.json();
      setData(sensorsData);
      if (alertsData.alerts && alertsData.alerts.length > 0 && !alertsData.alerts[0].acknowledged) {
        setLatestAlert(alertsData.alerts[0]);
      } else {
        setLatestAlert(null);
      }
    } catch (err) {
      console.error('Erreur API:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return (
      <div className="page">
        <div className="loading"><div className="spinner"></div></div>
      </div>
    );
  }

  const { sensors, system } = data;

  return (
    <div className="page">
      <div className="header">
        <div className="header-title">
          <span className="logo">🌿</span>
          <div>
            <h1>HydroNFT</h1>
            <div className="header-subtitle">Système NFT Intelligent</div>
          </div>
        </div>
      </div>

      {/* Jauges des capteurs en grille 2x2 */}
      <div className="gauge-grid">
        <GaugeCard
          label="pH" value={sensors.ph} unit="potentiel hydrogène"
          min={0} max={14} type="ph"
          optimalMin={5.5} optimalMax={6.5}
        />
        <GaugeCard
          label="EC" value={sensors.ec} unit="mS/cm"
          min={0} max={5} type="ec"
          optimalMin={0.8} optimalMax={2.2}
        />
        <GaugeCard
          label="Température" value={sensors.temperature} unit="°C"
          min={0} max={50} type="temp"
          optimalMin={18} optimalMax={24}
        />
        <GaugeCard
          label="Niveau d'eau" value={sensors.water_level} unit="%"
          min={0} max={100} type="water"
          optimalMin={25} optimalMax={100}
        />
      </div>

      {/* Statuts du système */}
      <div className="status-chips">
        <div className="status-chip">
          <span className={`status-dot ${system.pump_on ? 'on' : 'off'}`}></span>
          Pompe {system.pump_on ? 'ON' : 'OFF'}
        </div>
        <div className="status-chip">
          <span className={`status-dot ${system.lighting_on ? 'on' : 'off'}`}></span>
          Éclairage {system.lighting_on ? 'ON' : 'OFF'}
        </div>
        <div className="status-chip">
          <span className={`status-dot ${system.auto_mode ? 'auto' : 'off'}`}></span>
          {system.auto_mode ? 'Auto' : 'Manuel'}
        </div>
      </div>

      {/* Alerte la plus récente */}
      {latestAlert && (
        <div className={`alert-banner ${latestAlert.severity}`}>
          <span className="alert-icon">
            {latestAlert.severity === 'critical' ? '⚠️' : latestAlert.severity === 'warning' ? '⚡' : 'ℹ️'}
          </span>
          <span>{latestAlert.message}</span>
        </div>
      )}
    </div>
  );
}
