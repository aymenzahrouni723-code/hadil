/* ============================================================
   HydroNFT — Backend Server
   Express + sql.js (comme NurtureFlow)
   Simulation capteurs ESP32 integree
   ============================================================ */

const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const initSqlJs = require('sql.js');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = path.join(__dirname, 'hydronft.db');

let db;

// ── Helpers DB ──
function saveDB() {
  const data = db.export();
  fs.writeFileSync(DB_PATH, Buffer.from(data));
}

function queryAll(sql, params = []) {
  const stmt = db.prepare(sql);
  if (params.length) stmt.bind(params);
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  stmt.free();
  return rows;
}

function queryOne(sql, params = []) {
  const rows = queryAll(sql, params);
  return rows.length > 0 ? rows[0] : null;
}

function runSQL(sql, params = []) {
  db.run(sql, params);
  saveDB();
}

// ── Simulateur de capteurs ESP32 ──
const sensorState = {
  ph: 6.1,
  ec: 1.2,
  temperature: 21.0,
  water_level: 85,
  lastUpdate: null
};

function simulateSensors() {
  const hour = new Date().getHours();
  const isDay = hour >= 8 && hour < 20;

  // pH: oscille autour de 6.1 avec bruit gaussien
  const phNoise = (Math.random() - 0.5) * 0.15;
  sensorState.ph = Math.round((sensorState.ph + phNoise) * 100) / 100;
  if (sensorState.ph < 5.0) sensorState.ph = 5.0 + Math.random() * 0.3;
  if (sensorState.ph > 7.5) sensorState.ph = 7.5 - Math.random() * 0.3;
  // Tendance de retour vers 6.1
  sensorState.ph += (6.1 - sensorState.ph) * 0.05;
  sensorState.ph = Math.round(sensorState.ph * 100) / 100;

  // EC: varie autour de la valeur de la culture
  const ecNoise = (Math.random() - 0.5) * 0.08;
  sensorState.ec = Math.round((sensorState.ec + ecNoise) * 100) / 100;
  if (sensorState.ec < 0.5) sensorState.ec = 0.5 + Math.random() * 0.2;
  if (sensorState.ec > 3.0) sensorState.ec = 3.0 - Math.random() * 0.2;
  sensorState.ec += (1.2 - sensorState.ec) * 0.03;
  sensorState.ec = Math.round(sensorState.ec * 100) / 100;

  // Temperature: cycle jour/nuit
  const tempTarget = isDay ? 21 + Math.random() * 2 : 16 + Math.random() * 2;
  const tempNoise = (Math.random() - 0.5) * 0.3;
  sensorState.temperature += (tempTarget - sensorState.temperature) * 0.1 + tempNoise;
  sensorState.temperature = Math.round(sensorState.temperature * 10) / 10;

  // Niveau d'eau: descend lentement, remplissage auto a 20%
  sensorState.water_level -= Math.random() * 0.5;
  if (sensorState.water_level < 20) sensorState.water_level = 85 + Math.random() * 10;
  sensorState.water_level = Math.round(sensorState.water_level);

  sensorState.lastUpdate = new Date().toISOString();

  // Sauvegarder en DB
  try {
    db.run(
      'INSERT INTO sensor_readings (ph, ec, temperature, water_level, timestamp) VALUES (?, ?, ?, ?, ?)',
      [sensorState.ph, sensorState.ec, sensorState.temperature, sensorState.water_level, sensorState.lastUpdate]
    );
    saveDB();
  } catch (e) { /* ignore */ }
}

// ── Controle automatique ──
function checkAndControl() {
  try {
    const state = queryOne('SELECT * FROM system_state WHERE id = 1');
    if (!state || !state.auto_mode) return;

    const ph = sensorState.ph;
    const ec = sensorState.ec;
    let pumpShouldStop = false;

    // Verifier pH
    if (ph < state.ph_threshold_min || ph > state.ph_threshold_max) {
      pumpShouldStop = true;
      const sev = (ph < state.ph_threshold_min - 0.5 || ph > state.ph_threshold_max + 0.5) ? 'critical' : 'warning';
      const msg = `pH ${ph < state.ph_threshold_min ? 'trop bas' : 'trop eleve'}: ${ph} (seuil: ${state.ph_threshold_min}-${state.ph_threshold_max})`;
      createAlert('ph', sev, msg, ph, `${state.ph_threshold_min}-${state.ph_threshold_max}`);
    }

    // Verifier EC
    if (ec < state.ec_threshold_min || ec > state.ec_threshold_max) {
      pumpShouldStop = true;
      const sev = (ec < state.ec_threshold_min - 0.3 || ec > state.ec_threshold_max + 0.3) ? 'critical' : 'warning';
      const msg = `EC ${ec < state.ec_threshold_min ? 'trop basse' : 'trop elevee'}: ${ec} mS/cm (seuil: ${state.ec_threshold_min}-${state.ec_threshold_max})`;
      createAlert('ec', sev, msg, ec, `${state.ec_threshold_min}-${state.ec_threshold_max}`);
    }

    // Controle pompe
    if (pumpShouldStop && state.pump_on) {
      db.run("UPDATE system_state SET pump_on = 0, updated_at = ? WHERE id = 1", [new Date().toISOString()]);
      createAlert('pump', 'critical', 'Pompe arretee automatiquement (parametres hors plage)', null, null);
      saveDB();
    } else if (!pumpShouldStop && !state.pump_on && state.auto_mode) {
      db.run("UPDATE system_state SET pump_on = 1, updated_at = ? WHERE id = 1", [new Date().toISOString()]);
      saveDB();
    }

    // Niveau d'eau
    if (sensorState.water_level < 25) {
      const sev = sensorState.water_level < 10 ? 'critical' : 'warning';
      createAlert('water_level', sev, `Niveau d'eau bas: ${sensorState.water_level}%`, sensorState.water_level, '> 25%');
    }

    // Eclairage auto
    const culture = queryOne('SELECT * FROM culture_profiles WHERE id = ?', [state.active_culture_id]);
    if (culture) {
      const hour = new Date().getHours();
      const lightEnd = 8 + Math.floor(culture.light_hours_max);
      const shouldLight = hour >= 8 && hour < lightEnd;
      if (shouldLight && !state.lighting_on) {
        db.run("UPDATE system_state SET lighting_on = 1, updated_at = ? WHERE id = 1", [new Date().toISOString()]);
        saveDB();
      } else if (!shouldLight && state.lighting_on) {
        db.run("UPDATE system_state SET lighting_on = 0, updated_at = ? WHERE id = 1", [new Date().toISOString()]);
        saveDB();
      }
    }
  } catch (e) { console.error('[CTRL]', e.message); }
}

function createAlert(type, severity, message, value, threshold) {
  try {
    const existing = queryOne(
      "SELECT id FROM alerts WHERE type = ? AND message = ? AND timestamp > datetime('now', '-60 seconds')",
      [type, message]
    );
    if (existing) return;
    db.run(
      'INSERT INTO alerts (type, severity, message, value, threshold) VALUES (?, ?, ?, ?, ?)',
      [type, severity, message, value, threshold]
    );
    saveDB();
  } catch (e) { /* ignore duplicates */ }
}

// ── Start Server ──
async function startServer() {
  const SQL = await initSqlJs();

  if (fs.existsSync(DB_PATH)) {
    db = new SQL.Database(fs.readFileSync(DB_PATH));
  } else {
    db = new SQL.Database();
  }

  // Tables
  db.run(`CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ph REAL, ec REAL, temperature REAL, water_level REAL,
    timestamp TEXT DEFAULT (datetime('now'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS culture_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, emoji TEXT, description TEXT, nutrients TEXT,
    ph_min REAL, ph_max REAL, ec_min REAL, ec_max REAL,
    temp_min REAL, temp_max REAL, humidity_min REAL, humidity_max REAL,
    light_hours_min REAL, light_hours_max REAL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS system_state (
    id INTEGER PRIMARY KEY, pump_on INTEGER DEFAULT 1, lighting_on INTEGER DEFAULT 0,
    auto_mode INTEGER DEFAULT 1, active_culture_id INTEGER DEFAULT 1,
    ph_threshold_min REAL DEFAULT 5.5, ph_threshold_max REAL DEFAULT 6.5,
    ec_threshold_min REAL DEFAULT 0.8, ec_threshold_max REAL DEFAULT 1.4,
    updated_at TEXT DEFAULT (datetime('now'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, severity TEXT, message TEXT, value REAL, threshold TEXT,
    acknowledged INTEGER DEFAULT 0, timestamp TEXT DEFAULT (datetime('now'))
  )`);

  // Seed cultures
  const hasC = queryOne('SELECT COUNT(*) as c FROM culture_profiles');
  if (!hasC || hasC.c === 0) {
    db.run(`INSERT INTO culture_profiles VALUES (1,'Laitue','🥬','Culture hydroponique NFT ideale pour debutants. Cycle court de 30-45 jours.','N:150-200, P:50, K:150-200, Ca:200, Mg:50',5.5,6.5,0.8,1.4,18,22,50,70,10,14)`);
    db.run(`INSERT INTO culture_profiles VALUES (2,'Basilic','🌿','Herbe aromatique productive en NFT. Recolte en continu possible.','N:150-200, P:50-80, K:150-200, Ca:150, Mg:40',5.5,6.5,1.2,1.6,18,24,40,60,12,16)`);
    db.run(`INSERT INTO culture_profiles VALUES (3,'Fraise','🍓','Culture NFT possible avec varietes remontantes. Necessite EC plus elevee.','N:80-120, P:50-80, K:200-250, Ca:150, Mg:50',5.5,6.5,1.8,2.2,18,24,60,75,12,14)`);
  }

  const hasS = queryOne('SELECT COUNT(*) as c FROM system_state');
  if (!hasS || hasS.c === 0) {
    db.run('INSERT INTO system_state (id) VALUES (1)');
  }

  saveDB();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.static(__dirname, { extensions: ['html'] }));

  // ═══════ API CAPTEURS ═══════

  app.get('/api/sensors/current', (req, res) => {
    const state = queryOne('SELECT * FROM system_state WHERE id = 1');
    res.json({
      sensors: sensorState,
      system: state ? {
        pump_on: !!state.pump_on,
        lighting_on: !!state.lighting_on,
        auto_mode: !!state.auto_mode,
        active_culture_id: state.active_culture_id
      } : {}
    });
  });

  app.get('/api/sensors/history', (req, res) => {
    const hours = parseInt(req.query.hours) || 24;
    const limit = parseInt(req.query.limit) || 500;
    const readings = queryAll(
      `SELECT ph, ec, temperature, water_level, timestamp FROM sensor_readings WHERE timestamp > datetime('now', ?) ORDER BY timestamp ASC LIMIT ?`,
      [`-${hours} hours`, limit]
    );
    const stats = {};
    if (readings.length > 0) {
      ['ph', 'ec', 'temperature', 'water_level'].forEach(k => {
        const vals = readings.map(r => r[k]);
        stats[k] = {
          min: Math.round(Math.min(...vals) * 100) / 100,
          max: Math.round(Math.max(...vals) * 100) / 100,
          avg: Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 100) / 100
        };
      });
    }
    res.json({ history: readings, stats });
  });

  // ═══════ API CULTURES ═══════

  app.get('/api/cultures', (req, res) => {
    const cultures = queryAll('SELECT * FROM culture_profiles ORDER BY id');
    const state = queryOne('SELECT active_culture_id FROM system_state WHERE id = 1');
    const activeId = state ? state.active_culture_id : 1;
    res.json({ cultures, active_culture_id: activeId });
  });

  app.post('/api/cultures/:id/activate', (req, res) => {
    const id = parseInt(req.params.id);
    const culture = queryOne('SELECT * FROM culture_profiles WHERE id = ?', [id]);
    if (!culture) return res.status(404).json({ error: 'Non trouve' });
    runSQL(
      'UPDATE system_state SET active_culture_id=?, ph_threshold_min=?, ph_threshold_max=?, ec_threshold_min=?, ec_threshold_max=?, updated_at=? WHERE id=1',
      [id, culture.ph_min, culture.ph_max, culture.ec_min, culture.ec_max, new Date().toISOString()]
    );
    res.json({ message: `Culture ${culture.name} activee`, thresholds: { ph_min: culture.ph_min, ph_max: culture.ph_max, ec_min: culture.ec_min, ec_max: culture.ec_max } });
  });

  // ═══════ API CONTROLE ═══════

  app.post('/api/pump/toggle', (req, res) => {
    const state = queryOne('SELECT pump_on FROM system_state WHERE id = 1');
    const newVal = state.pump_on ? 0 : 1;
    runSQL('UPDATE system_state SET pump_on=?, updated_at=? WHERE id=1', [newVal, new Date().toISOString()]);
    res.json({ pump_on: !!newVal });
  });

  app.post('/api/lighting/toggle', (req, res) => {
    const state = queryOne('SELECT lighting_on FROM system_state WHERE id = 1');
    const newVal = state.lighting_on ? 0 : 1;
    runSQL('UPDATE system_state SET lighting_on=?, updated_at=? WHERE id=1', [newVal, new Date().toISOString()]);
    res.json({ lighting_on: !!newVal });
  });

  app.get('/api/system/status', (req, res) => {
    const state = queryOne('SELECT * FROM system_state WHERE id = 1');
    const culture = state ? queryOne('SELECT name, emoji FROM culture_profiles WHERE id = ?', [state.active_culture_id]) : null;
    const unread = queryOne('SELECT COUNT(*) as count FROM alerts WHERE acknowledged = 0');
    res.json({
      pump_on: state ? !!state.pump_on : false,
      lighting_on: state ? !!state.lighting_on : false,
      auto_mode: state ? !!state.auto_mode : true,
      active_culture: state ? { id: state.active_culture_id, name: culture ? culture.name : 'Inconnue', emoji: culture ? culture.emoji : '' } : {},
      thresholds: state ? { ph_min: state.ph_threshold_min, ph_max: state.ph_threshold_max, ec_min: state.ec_threshold_min, ec_max: state.ec_threshold_max } : {},
      unread_alerts: unread ? unread.count : 0
    });
  });

  app.post('/api/system/mode', (req, res) => {
    const autoMode = req.body.auto_mode ? 1 : 0;
    runSQL('UPDATE system_state SET auto_mode=?, updated_at=? WHERE id=1', [autoMode, new Date().toISOString()]);
    res.json({ auto_mode: !!autoMode });
  });

  app.post('/api/settings/thresholds', (req, res) => {
    const d = req.body;
    const updates = [];
    const vals = [];
    if (d.ph_min !== undefined) { updates.push('ph_threshold_min=?'); vals.push(parseFloat(d.ph_min)); }
    if (d.ph_max !== undefined) { updates.push('ph_threshold_max=?'); vals.push(parseFloat(d.ph_max)); }
    if (d.ec_min !== undefined) { updates.push('ec_threshold_min=?'); vals.push(parseFloat(d.ec_min)); }
    if (d.ec_max !== undefined) { updates.push('ec_threshold_max=?'); vals.push(parseFloat(d.ec_max)); }
    if (updates.length > 0) {
      vals.push(new Date().toISOString());
      runSQL(`UPDATE system_state SET ${updates.join(',')}, updated_at=? WHERE id=1`, vals);
    }
    res.json({ message: 'Seuils mis a jour' });
  });

  // ═══════ API ALERTES ═══════

  app.get('/api/alerts', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;
    const alerts = queryAll('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?', [limit]);
    res.json({ alerts });
  });

  app.post('/api/alerts/:id/acknowledge', (req, res) => {
    runSQL('UPDATE alerts SET acknowledged = 1 WHERE id = ?', [parseInt(req.params.id)]);
    res.json({ message: 'OK' });
  });

  app.post('/api/alerts/acknowledge-all', (req, res) => {
    runSQL('UPDATE alerts SET acknowledged = 1 WHERE acknowledged = 0');
    res.json({ message: 'OK' });
  });

  // ── Demarrer la simulation ──
  setInterval(() => { simulateSensors(); checkAndControl(); }, 5000);
  simulateSensors(); // Premiere lecture immediate

  // ── Lancer le serveur ──
  app.listen(PORT, () => {
    console.log('============================================================');
    console.log('  HydroNFT - Systeme Hydroponique NFT Intelligent');
    console.log(`  http://localhost:${PORT}`);
    console.log('============================================================');
  });
}

startServer().catch(console.error);
