"""
HydroNFT - Serveur Backend Flask
API REST pour le système hydroponique NFT intelligent
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time
import os

from models import init_db, get_db
from sensor_simulator import SensorSimulator
from control_logic import ControlLogic

# Dossier des fichiers statiques (frontend React compilé)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app)

# Initialiser le simulateur et la logique de contrôle
simulator = SensorSimulator()
controller = ControlLogic(simulator)


# ===== THREAD DE CONTRÔLE AUTOMATIQUE =====
def control_loop():
    """Boucle de vérification et contrôle automatique (toutes les 5s)."""
    while True:
        try:
            controller.check_and_control()
        except Exception as e:
            print(f"[CONTRÔLE] Erreur: {e}")
        time.sleep(5)


# ===== API CAPTEURS =====

@app.route('/api/sensors/current', methods=['GET'])
def get_current_sensors():
    """Obtenir les dernières valeurs des capteurs."""
    values = simulator.get_current_values()

    # Ajouter l'état du système
    conn = get_db()
    state = conn.execute("SELECT * FROM system_state WHERE id = 1").fetchone()
    conn.close()

    return jsonify({
        'sensors': values,
        'system': {
            'pump_on': bool(state['pump_on']),
            'lighting_on': bool(state['lighting_on']),
            'auto_mode': bool(state['auto_mode']),
            'active_culture_id': state['active_culture_id']
        } if state else {}
    })


@app.route('/api/sensors/history', methods=['GET'])
def get_sensor_history():
    """Obtenir l'historique des lectures (dernières 24h par défaut)."""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 500, type=int)

    conn = get_db()
    readings = conn.execute('''
        SELECT ph, ec, temperature, water_level, timestamp
        FROM sensor_readings
        WHERE timestamp > datetime('now', ?)
        ORDER BY timestamp ASC
        LIMIT ?
    ''', (f'-{hours} hours', limit)).fetchall()
    conn.close()

    data = [{
        'ph': r['ph'],
        'ec': r['ec'],
        'temperature': r['temperature'],
        'water_level': r['water_level'],
        'timestamp': r['timestamp']
    } for r in readings]

    # Calculer les statistiques
    if data:
        stats = {
            'ph': _calc_stats([d['ph'] for d in data]),
            'ec': _calc_stats([d['ec'] for d in data]),
            'temperature': _calc_stats([d['temperature'] for d in data]),
            'water_level': _calc_stats([d['water_level'] for d in data]),
        }
    else:
        stats = {}

    return jsonify({'history': data, 'stats': stats})


def _calc_stats(values):
    """Calculer min, max, moyenne."""
    if not values:
        return {'min': 0, 'max': 0, 'avg': 0}
    return {
        'min': round(min(values), 2),
        'max': round(max(values), 2),
        'avg': round(sum(values) / len(values), 2)
    }


# ===== API CULTURES =====

@app.route('/api/cultures', methods=['GET'])
def get_cultures():
    """Obtenir la liste des profils de cultures."""
    conn = get_db()
    cultures = conn.execute("SELECT * FROM culture_profiles ORDER BY id").fetchall()
    state = conn.execute("SELECT active_culture_id FROM system_state WHERE id = 1").fetchone()
    conn.close()

    active_id = state['active_culture_id'] if state else 1

    return jsonify({
        'cultures': [{
            'id': c['id'],
            'name': c['name'],
            'emoji': c['emoji'],
            'ph_min': c['ph_min'], 'ph_max': c['ph_max'],
            'ec_min': c['ec_min'], 'ec_max': c['ec_max'],
            'temp_min': c['temp_min'], 'temp_max': c['temp_max'],
            'humidity_min': c['humidity_min'], 'humidity_max': c['humidity_max'],
            'light_hours_min': c['light_hours_min'], 'light_hours_max': c['light_hours_max'],
            'nutrients': c['nutrients'],
            'description': c['description'],
            'active': c['id'] == active_id
        } for c in cultures],
        'active_culture_id': active_id
    })


@app.route('/api/cultures/<int:culture_id>/activate', methods=['POST'])
def activate_culture(culture_id):
    """Activer une culture et ajuster les seuils automatiquement."""
    conn = get_db()
    culture = conn.execute("SELECT * FROM culture_profiles WHERE id = ?", (culture_id,)).fetchone()
    if not culture:
        conn.close()
        return jsonify({'error': 'Culture non trouvée'}), 404

    conn.execute('''
        UPDATE system_state SET
            active_culture_id = ?,
            ph_threshold_min = ?,
            ph_threshold_max = ?,
            ec_threshold_min = ?,
            ec_threshold_max = ?,
            updated_at = ?
        WHERE id = 1
    ''', (culture_id, culture['ph_min'], culture['ph_max'],
          culture['ec_min'], culture['ec_max'], datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({
        'message': f'Culture {culture["name"]} activée',
        'thresholds': {
            'ph_min': culture['ph_min'], 'ph_max': culture['ph_max'],
            'ec_min': culture['ec_min'], 'ec_max': culture['ec_max']
        }
    })


# ===== API CONTRÔLE =====

@app.route('/api/pump/toggle', methods=['POST'])
def toggle_pump():
    """Démarrer/arrêter la pompe (cas d'utilisation: démarrer/arrêter la pompe)."""
    conn = get_db()
    state = conn.execute("SELECT pump_on FROM system_state WHERE id = 1").fetchone()
    new_state = 0 if state['pump_on'] else 1
    conn.execute("UPDATE system_state SET pump_on = ?, updated_at = ? WHERE id = 1",
                 (new_state, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'pump_on': bool(new_state)})


@app.route('/api/lighting/toggle', methods=['POST'])
def toggle_lighting():
    """Contrôler l'éclairage LED."""
    conn = get_db()
    state = conn.execute("SELECT lighting_on FROM system_state WHERE id = 1").fetchone()
    new_state = 0 if state['lighting_on'] else 1
    conn.execute("UPDATE system_state SET lighting_on = ?, updated_at = ? WHERE id = 1",
                 (new_state, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'lighting_on': bool(new_state)})


@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Obtenir l'état complet du système."""
    conn = get_db()
    state = conn.execute("SELECT * FROM system_state WHERE id = 1").fetchone()
    culture = conn.execute(
        "SELECT name, emoji FROM culture_profiles WHERE id = ?",
        (state['active_culture_id'],)
    ).fetchone() if state else None

    # Compter les alertes non acquittées
    unread = conn.execute(
        "SELECT COUNT(*) as count FROM alerts WHERE acknowledged = 0"
    ).fetchone()
    conn.close()

    return jsonify({
        'pump_on': bool(state['pump_on']) if state else False,
        'lighting_on': bool(state['lighting_on']) if state else False,
        'auto_mode': bool(state['auto_mode']) if state else True,
        'active_culture': {
            'id': state['active_culture_id'],
            'name': culture['name'] if culture else 'Inconnue',
            'emoji': culture['emoji'] if culture else '🌱'
        } if state else {},
        'thresholds': {
            'ph_min': state['ph_threshold_min'],
            'ph_max': state['ph_threshold_max'],
            'ec_min': state['ec_threshold_min'],
            'ec_max': state['ec_threshold_max']
        } if state else {},
        'unread_alerts': unread['count'] if unread else 0
    })


@app.route('/api/system/mode', methods=['POST'])
def set_system_mode():
    """Basculer entre mode automatique et mode manuel."""
    data = request.get_json() or {}
    auto_mode = data.get('auto_mode', True)
    conn = get_db()
    conn.execute("UPDATE system_state SET auto_mode = ?, updated_at = ? WHERE id = 1",
                 (1 if auto_mode else 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'auto_mode': auto_mode})


@app.route('/api/settings/thresholds', methods=['POST'])
def set_thresholds():
    """Régler les consignes PH/EC (cas d'utilisation: régler les consignes)."""
    data = request.get_json() or {}
    conn = get_db()

    updates = {}
    if 'ph_min' in data:
        updates['ph_threshold_min'] = float(data['ph_min'])
    if 'ph_max' in data:
        updates['ph_threshold_max'] = float(data['ph_max'])
    if 'ec_min' in data:
        updates['ec_threshold_min'] = float(data['ec_min'])
    if 'ec_max' in data:
        updates['ec_threshold_max'] = float(data['ec_max'])

    if updates:
        set_clause = ', '.join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [datetime.now().isoformat()]
        conn.execute(f"UPDATE system_state SET {set_clause}, updated_at = ? WHERE id = 1", values)
        conn.commit()

    conn.close()
    return jsonify({'message': 'Seuils mis à jour', 'thresholds': updates})


# ===== API ALERTES =====

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Obtenir la liste des alertes."""
    limit = request.args.get('limit', 50, type=int)
    conn = get_db()
    alerts = conn.execute('''
        SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()

    return jsonify({
        'alerts': [{
            'id': a['id'],
            'type': a['type'],
            'severity': a['severity'],
            'message': a['message'],
            'value': a['value'],
            'threshold': a['threshold'],
            'acknowledged': bool(a['acknowledged']),
            'timestamp': a['timestamp']
        } for a in alerts]
    })


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acquitter une alerte."""
    conn = get_db()
    conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Alerte acquittée'})


@app.route('/api/alerts/acknowledge-all', methods=['POST'])
def acknowledge_all_alerts():
    """Acquitter toutes les alertes."""
    conn = get_db()
    conn.execute("UPDATE alerts SET acknowledged = 1 WHERE acknowledged = 0")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Toutes les alertes acquittées'})


# ===== FRONTEND (fichiers statiques React) =====

@app.route('/')
def serve_frontend():
    """Servir la page principale du frontend React."""
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Servir les fichiers statiques ou retourner index.html pour le routing React."""
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, 'index.html')


# ===== INITIALISATION (fonctionne avec gunicorn ET python direct) =====

def start_background_services():
    """Initialiser la DB, le simulateur et le controle automatique."""
    init_db()
    simulator.start()
    control_thread = threading.Thread(target=control_loop, daemon=True)
    control_thread.start()


# Demarrer les services au chargement du module (pour gunicorn)
start_background_services()


if __name__ == '__main__':
    print("=" * 60)
    print("  HydroNFT - Systeme Hydroponique NFT Intelligent")
    print("  Backend API REST")
    print("  http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
