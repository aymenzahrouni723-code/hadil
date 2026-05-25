import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Filler, Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler, Legend);

const API_URL = '/api';

const TABS = [
  { key: 'ph', label: 'pH', color: '#2ECC71', unit: '' },
  { key: 'ec', label: 'EC', color: '#3498DB', unit: ' mS/cm' },
  { key: 'temperature', label: 'Température', color: '#E67E22', unit: '°C' },
  { key: 'water_level', label: 'Niveau d\'eau', color: '#1ABC9C', unit: '%' },
];

export default function History() {
  const [activeTab, setActiveTab] = useState('ph');
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({});

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/sensors/history?hours=1&limit=200`);
      const data = await res.json();
      setHistory(data.history || []);
      setStats(data.stats || {});
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  const tab = TABS.find(t => t.key === activeTab);
  const currentStats = stats[activeTab] || { min: 0, max: 0, avg: 0 };

  const chartData = {
    labels: history.map(h => {
      const d = new Date(h.timestamp);
      return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    }),
    datasets: [{
      label: tab.label,
      data: history.map(h => h[activeTab]),
      borderColor: tab.color,
      backgroundColor: tab.color + '15',
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { intersect: false, mode: 'index' },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#F8FAFC',
        bodyColor: '#94A3B8',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        callbacks: {
          label: (ctx) => `${tab.label}: ${ctx.parsed.y}${tab.unit}`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#64748B', maxTicksLimit: 8, font: { size: 10 } },
        grid: { color: 'rgba(255,255,255,0.04)' }
      },
      y: {
        ticks: { color: '#64748B', font: { size: 10 } },
        grid: { color: 'rgba(255,255,255,0.04)' }
      }
    }
  };

  return (
    <div className="page">
      <h2 className="page-title">📈 Historique</h2>

      {/* Tabs des capteurs */}
      <div className="chart-tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`chart-tab ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Graphique */}
      <div className="chart-container">
        {history.length > 0 ? (
          <Line data={chartData} options={chartOptions} />
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <p>Données en cours de collecte...</p>
          </div>
        )}
      </div>

      {/* Statistiques */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{currentStats.avg}{tab.unit}</div>
          <div className="stat-label">Moyenne</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#E74C3C' }}>{currentStats.min}{tab.unit}</div>
          <div className="stat-label">Minimum</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#3498DB' }}>{currentStats.max}{tab.unit}</div>
          <div className="stat-label">Maximum</div>
        </div>
      </div>
    </div>
  );
}
