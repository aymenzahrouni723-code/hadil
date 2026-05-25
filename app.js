/* ============================================================
   HydroNFT — Frontend App (Vanilla JS)
   ============================================================ */

const API = '/api';
let currentScreen = 'dashboard';
let historyChart = null;
let activeChartTab = 'ph';

// ═══════ NAVIGATION ═══════

function navigateTo(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(`screen-${screen}`).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`.nav-item[data-nav="${screen}"]`)?.classList.add('active');
  currentScreen = screen;

  if (screen === 'dashboard') loadDashboard();
  else if (screen === 'control') loadControl();
  else if (screen === 'cultures') loadCultures();
  else if (screen === 'history') loadHistory();
  else if (screen === 'alerts') loadAlerts();
}

// ═══════ GAUGE COMPONENT ═══════

function createGauge(type, label, value, unit, min, max, optMin, optMax) {
  const colors = { ph: '#2ECC71', ec: '#3498DB', temp: '#E67E22', water: '#1ABC9C' };
  const color = colors[type] || '#2ECC71';
  const r = 40, circ = 2 * Math.PI * r;
  const norm = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const offset = circ - norm * circ;
  const isOk = (optMin === undefined || optMax === undefined) ? true : (value >= optMin && value <= optMax);
  const fillColor = isOk ? color : '#E74C3C';

  return `<div class="gauge-card ${type}">
    <div class="gauge-svg-wrap">
      <svg class="gauge-svg" viewBox="0 0 100 100">
        <circle class="gauge-bg" cx="50" cy="50" r="${r}"/>
        <circle class="gauge-fill" cx="50" cy="50" r="${r}"
          style="stroke:${fillColor};stroke-dasharray:${circ};stroke-dashoffset:${offset};filter:drop-shadow(0 0 6px ${fillColor}40)"/>
      </svg>
      <div class="gauge-val" style="color:${fillColor}">${value}</div>
    </div>
    <div class="gauge-label">${label}</div>
    <div class="gauge-unit">${unit}</div>
  </div>`;
}

// ═══════ DASHBOARD ═══════

async function loadDashboard() {
  try {
    const [sensorsRes, alertsRes] = await Promise.all([
      fetch(`${API}/sensors/current`),
      fetch(`${API}/alerts?limit=1`)
    ]);
    const data = await sensorsRes.json();
    const alertsData = await alertsRes.json();
    const { sensors, system } = data;

    // Gauges
    document.getElementById('gauge-grid').innerHTML =
      createGauge('ph', 'pH', sensors.ph, 'potentiel hydrogene', 0, 14, 5.5, 6.5) +
      createGauge('ec', 'EC', sensors.ec, 'mS/cm', 0, 5, 0.8, 2.2) +
      createGauge('temp', 'Temperature', sensors.temperature, '°C', 0, 50, 18, 24) +
      createGauge('water', "Niveau d'eau", sensors.water_level, '%', 0, 100, 25, 100);

    // Status chips
    document.getElementById('status-chips').innerHTML = `
      <div class="status-chip"><span class="status-dot ${system.pump_on ? 'on' : 'off'}"></span>Pompe ${system.pump_on ? 'ON' : 'OFF'}</div>
      <div class="status-chip"><span class="status-dot ${system.lighting_on ? 'on' : 'off'}"></span>Eclairage ${system.lighting_on ? 'ON' : 'OFF'}</div>
      <div class="status-chip"><span class="status-dot ${system.auto_mode ? 'auto' : 'off'}"></span>${system.auto_mode ? 'Auto' : 'Manuel'}</div>`;

    // Latest alert
    const el = document.getElementById('latest-alert');
    if (alertsData.alerts?.length > 0 && !alertsData.alerts[0].acknowledged) {
      const a = alertsData.alerts[0];
      const icon = a.severity === 'critical' ? '⚠️' : '⚡';
      el.innerHTML = `<div class="alert-banner ${a.severity}"><span>${icon}</span><span>${a.message}</span></div>`;
    } else {
      el.innerHTML = '';
    }
  } catch (e) {
    console.error('Dashboard error:', e);
  }
}

// ═══════ CONTROL ═══════

async function loadControl() {
  try {
    const res = await fetch(`${API}/system/status`);
    const s = await res.json();

    document.getElementById('mode-toggle').innerHTML = `
      <button class="mode-btn ${s.auto_mode ? 'active' : ''}" onclick="setMode(true)">🤖 Automatique</button>
      <button class="mode-btn ${!s.auto_mode ? 'active' : ''}" onclick="setMode(false)">✋ Manuel</button>`;

    document.getElementById('control-toggles').innerHTML = `
      <div class="toggle-card">
        <div class="toggle-info">
          <div class="toggle-icon">💧</div>
          <div><div class="toggle-label">Pompe a eau (600L/H)</div><div class="toggle-sub">${s.auto_mode ? 'Automatique' : 'Manuel'}</div></div>
        </div>
        <div class="toggle-switch ${s.pump_on ? 'active' : ''}" onclick="togglePump()"><div class="knob"></div></div>
      </div>
      <div class="toggle-card">
        <div class="toggle-info">
          <div class="toggle-icon">💡</div>
          <div><div class="toggle-label">Eclairage LED</div><div class="toggle-sub">${s.auto_mode ? 'Automatique' : 'Manuel'}</div></div>
        </div>
        <div class="toggle-switch ${s.lighting_on ? 'active' : ''}" onclick="toggleLighting()"><div class="knob"></div></div>
      </div>`;

    const t = s.thresholds;
    document.getElementById('slider-section').innerHTML = `<h3>📐 Consignes</h3>
      ${slider('ph_min', 'Seuil pH min', t.ph_min, 4, 7, 0.1)}
      ${slider('ph_max', 'Seuil pH max', t.ph_max, 5, 9, 0.1)}
      ${slider('ec_min', 'Seuil EC min (mS/cm)', t.ec_min, 0.2, 3, 0.1)}
      ${slider('ec_max', 'Seuil EC max (mS/cm)', t.ec_max, 1, 5, 0.1)}`;
  } catch (e) { console.error('Control error:', e); }
}

function slider(key, label, val, min, max, step) {
  return `<div class="slider-group">
    <div class="slider-label"><span>${label}</span><span class="slider-value" id="sv-${key}">${val}</span></div>
    <input type="range" min="${min}" max="${max}" step="${step}" value="${val}"
      oninput="document.getElementById('sv-${key}').textContent=this.value"
      onchange="updateThreshold('${key}',this.value)"/>
  </div>`;
}

async function togglePump() { await fetch(`${API}/pump/toggle`, { method: 'POST' }); loadControl(); }
async function toggleLighting() { await fetch(`${API}/lighting/toggle`, { method: 'POST' }); loadControl(); }
async function setMode(auto) {
  await fetch(`${API}/system/mode`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ auto_mode: auto }) });
  loadControl();
}
async function updateThreshold(key, val) {
  await fetch(`${API}/settings/thresholds`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ [key]: parseFloat(val) }) });
}

// ═══════ CULTURES ═══════

async function loadCultures() {
  try {
    const res = await fetch(`${API}/cultures`);
    const data = await res.json();
    const activeId = data.active_culture_id;

    document.getElementById('cultures-list').innerHTML = data.cultures.map(c => `
      <div class="culture-card ${c.id === activeId ? 'active' : ''}">
        <div class="culture-header">
          <div class="culture-name"><span class="culture-emoji">${c.emoji}</span><span class="culture-title">${c.name}</span></div>
          ${c.id === activeId ? '<span class="culture-badge active">✅ Active</span>' : ''}
        </div>
        <div class="culture-params">
          <div class="culture-param"><span class="culture-param-label">pH</span><span class="culture-param-value">${c.ph_min} - ${c.ph_max}</span></div>
          <div class="culture-param"><span class="culture-param-label">EC (mS/cm)</span><span class="culture-param-value">${c.ec_min} - ${c.ec_max}</span></div>
          <div class="culture-param"><span class="culture-param-label">Temperature</span><span class="culture-param-value">${c.temp_min} - ${c.temp_max}°C</span></div>
          <div class="culture-param"><span class="culture-param-label">Humidite</span><span class="culture-param-value">${c.humidity_min} - ${c.humidity_max}%</span></div>
          <div class="culture-param"><span class="culture-param-label">Lumiere</span><span class="culture-param-value">${c.light_hours_min} - ${c.light_hours_max}h</span></div>
        </div>
        <p style="font-size:0.78rem;color:var(--text-tertiary);margin-bottom:14px;line-height:1.5;">${c.description}</p>
        <button class="culture-btn ${c.id === activeId ? 'active-btn' : ''}"
          onclick="activateCulture(${c.id})" ${c.id === activeId ? 'disabled' : ''}>
          ${c.id === activeId ? '✅ Culture Active' : 'Selectionner'}
        </button>
      </div>
    `).join('');
  } catch (e) { console.error('Cultures error:', e); }
}

async function activateCulture(id) {
  await fetch(`${API}/cultures/${id}/activate`, { method: 'POST' });
  loadCultures();
}

// ═══════ HISTORY ═══════

const TABS = [
  { key: 'ph', label: 'pH', color: '#2ECC71', unit: '' },
  { key: 'ec', label: 'EC', color: '#3498DB', unit: ' mS/cm' },
  { key: 'temperature', label: 'Temp', color: '#E67E22', unit: '°C' },
  { key: 'water_level', label: 'Eau', color: '#1ABC9C', unit: '%' }
];

async function loadHistory() {
  // Tabs
  document.getElementById('chart-tabs').innerHTML = TABS.map(t =>
    `<button class="chart-tab ${activeChartTab === t.key ? 'active' : ''}"
      onclick="activeChartTab='${t.key}';loadHistory()">${t.label}</button>`
  ).join('');

  try {
    const res = await fetch(`${API}/sensors/history?hours=1&limit=200`);
    const data = await res.json();
    const tab = TABS.find(t => t.key === activeChartTab);
    const st = data.stats[activeChartTab] || { min: 0, max: 0, avg: 0 };

    // Stats
    document.getElementById('stats-grid').innerHTML = `
      <div class="stat-card"><div class="stat-value">${st.avg}${tab.unit}</div><div class="stat-label">Moyenne</div></div>
      <div class="stat-card"><div class="stat-value" style="color:#E74C3C">${st.min}${tab.unit}</div><div class="stat-label">Minimum</div></div>
      <div class="stat-card"><div class="stat-value" style="color:#3498DB">${st.max}${tab.unit}</div><div class="stat-label">Maximum</div></div>`;

    // Chart
    const canvas = document.getElementById('historyChart');
    if (historyChart) historyChart.destroy();

    if (data.history.length === 0) {
      canvas.parentElement.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>Donnees en cours de collecte...</p></div><canvas id="historyChart" style="display:none;"></canvas>';
      return;
    }

    historyChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.history.map(h => new Date(h.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })),
        datasets: [{
          label: tab.label,
          data: data.history.map(h => h[activeChartTab]),
          borderColor: tab.color, backgroundColor: tab.color + '15',
          fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(17,24,39,0.95)', titleColor: '#F8FAFC',
            bodyColor: '#94A3B8', borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1, cornerRadius: 8, padding: 12,
            callbacks: { label: ctx => `${tab.label}: ${ctx.parsed.y}${tab.unit}` }
          }
        },
        scales: {
          x: { ticks: { color: '#64748B', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
          y: { ticks: { color: '#64748B', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  } catch (e) { console.error('History error:', e); }
}

// ═══════ ALERTS ═══════

async function loadAlerts() {
  try {
    const res = await fetch(`${API}/alerts?limit=50`);
    const data = await res.json();
    const alerts = data.alerts || [];
    const unread = alerts.filter(a => !a.acknowledged).length;

    document.getElementById('alert-badge').style.display = unread > 0 ? '' : 'none';
    document.getElementById('alert-badge').textContent = unread;
    document.getElementById('ack-all-btn').style.display = unread > 0 ? '' : 'none';

    if (alerts.length === 0) {
      document.getElementById('alerts-list').innerHTML = '<div class="empty-state"><div class="empty-icon">✅</div><p>Aucune alerte</p><p style="font-size:0.8rem;margin-top:8px;">Le systeme fonctionne normalement</p></div>';
      return;
    }

    document.getElementById('alerts-list').innerHTML = alerts.map(a => {
      const icon = a.severity === 'critical' ? '⚠️' : a.type === 'water_level' ? '💧' : a.type === 'temperature' ? '🌡️' : a.type === 'ph' ? '🧪' : a.type === 'pump' ? '🔧' : '⚡';
      const time = new Date(a.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      return `<div class="alert-card ${a.severity} ${a.acknowledged ? 'acknowledged' : ''}">
        <div class="alert-card-header">
          <div class="alert-message">${icon} ${a.message}</div>
          <span class="alert-time">${time}</span>
        </div>
        ${a.threshold ? `<div class="alert-threshold">Seuil: ${a.threshold}</div>` : ''}
        ${!a.acknowledged ? `<button class="alert-ack-btn" onclick="ackAlert(${a.id})">Acquitter</button>` : ''}
      </div>`;
    }).join('');
  } catch (e) { console.error('Alerts error:', e); }
}

async function ackAlert(id) {
  await fetch(`${API}/alerts/${id}/acknowledge`, { method: 'POST' });
  loadAlerts();
}

async function ackAllAlerts() {
  await fetch(`${API}/alerts/acknowledge-all`, { method: 'POST' });
  loadAlerts();
}

// ═══════ ALERT BADGE (navbar) ═══════

async function updateAlertBadge() {
  try {
    const res = await fetch(`${API}/system/status`);
    const data = await res.json();
    const el = document.getElementById('nav-alert-badge');
    if (data.unread_alerts > 0) {
      el.innerHTML = `<span class="nav-badge">${data.unread_alerts}</span>`;
    } else {
      el.innerHTML = '';
    }
  } catch (e) { /* ignore */ }
}

// ═══════ INIT ═══════

window.addEventListener('DOMContentLoaded', () => {
  // Splash screen
  setTimeout(() => {
    document.getElementById('splash').classList.add('hide');
    document.getElementById('navbar').style.display = 'flex';
    loadDashboard();
  }, 1500);

  // Auto-refresh
  setInterval(() => {
    if (currentScreen === 'dashboard') loadDashboard();
    updateAlertBadge();
  }, 3000);

  setInterval(() => {
    if (currentScreen === 'history') loadHistory();
  }, 10000);
});
