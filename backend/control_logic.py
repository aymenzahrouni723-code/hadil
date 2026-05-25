"""
HydroNFT - Logique de contrôle automatique
Correspond au diagramme de cas d'utilisation du rapport PFE:
- Contrôler automatiquement la pompe
- Contrôler automatiquement l'éclairage
- Émettre alerte visuelle/sonore (LED/Buzzer)
"""

from datetime import datetime
from models import get_db


class ControlLogic:
    """
    Logique de contrôle automatique du système hydroponique NFT.
    Basée sur les spécifications du rapport PFE et le diagramme de cas d'utilisation.
    """

    def __init__(self, simulator):
        self.simulator = simulator

    def check_and_control(self):
        """
        Vérifier les valeurs des capteurs et agir en conséquence.
        Appelé périodiquement par le serveur.
        
        Retourne la liste des alertes générées.
        """
        conn = get_db()
        alerts = []

        # Récupérer l'état du système
        state = conn.execute("SELECT * FROM system_state WHERE id = 1").fetchone()
        if not state:
            conn.close()
            return alerts

        # Si mode automatique désactivé, ne pas contrôler
        if not state['auto_mode']:
            conn.close()
            return alerts

        values = self.simulator.get_current_values()
        ph = values['ph']
        ec = values['ec']
        temp = values['temperature']
        water_level = values['water_level']

        # Récupérer les seuils configurés
        ph_min = state['ph_threshold_min']
        ph_max = state['ph_threshold_max']
        ec_min = state['ec_threshold_min']
        ec_max = state['ec_threshold_max']

        # --- Contrôle de la pompe ---
        # "La pompe est arrêtée si: pH hors-plage, EC trop bas ou trop élevée" (rapport ch.4)
        pump_should_stop = False
        
        if ph < ph_min or ph > ph_max:
            pump_should_stop = True
            severity = 'critical' if (ph < ph_min - 0.5 or ph > ph_max + 0.5) else 'warning'
            alert = self._create_alert(
                conn, 'ph',  severity,
                f'pH {"trop bas" if ph < ph_min else "trop élevé"}: {ph} (seuil: {ph_min}-{ph_max})',
                ph, f'{ph_min}-{ph_max}'
            )
            if alert:
                alerts.append(alert)

        if ec < ec_min or ec > ec_max:
            pump_should_stop = True
            severity = 'critical' if (ec < ec_min - 0.3 or ec > ec_max + 0.3) else 'warning'
            alert = self._create_alert(
                conn, 'ec', severity,
                f'EC {"trop basse" if ec < ec_min else "trop élevée"}: {ec} mS/cm (seuil: {ec_min}-{ec_max})',
                ec, f'{ec_min}-{ec_max}'
            )
            if alert:
                alerts.append(alert)

        # Contrôle automatique de la pompe
        if pump_should_stop and state['pump_on']:
            conn.execute("UPDATE system_state SET pump_on = 0, updated_at = ? WHERE id = 1",
                         (datetime.now().isoformat(),))
            alert = self._create_alert(
                conn, 'pump', 'critical',
                'Pompe arrêtée automatiquement (paramètres hors plage)',
                None, None
            )
            if alert:
                alerts.append(alert)
        elif not pump_should_stop and not state['pump_on'] and state['auto_mode']:
            conn.execute("UPDATE system_state SET pump_on = 1, updated_at = ? WHERE id = 1",
                         (datetime.now().isoformat(),))

        # --- Alerte niveau d'eau ---
        if water_level < 25:
            severity = 'critical' if water_level < 10 else 'warning'
            alert = self._create_alert(
                conn, 'water_level', severity,
                f'Niveau d\'eau bas: {water_level}% - Remplir le réservoir',
                water_level, '> 25%'
            )
            if alert:
                alerts.append(alert)

        # --- Alerte température ---
        # Récupérer les limites de la culture active
        culture = conn.execute(
            "SELECT * FROM culture_profiles WHERE id = ?",
            (state['active_culture_id'],)
        ).fetchone()

        if culture:
            if temp < culture['temp_min'] or temp > culture['temp_max']:
                severity = 'warning'
                alert = self._create_alert(
                    conn, 'temperature', severity,
                    f'Température {"basse" if temp < culture["temp_min"] else "élevée"}: '
                    f'{temp}°C (optimal: {culture["temp_min"]}-{culture["temp_max"]}°C)',
                    temp, f'{culture["temp_min"]}-{culture["temp_max"]}°C'
                )
                if alert:
                    alerts.append(alert)

        # --- Contrôle automatique de l'éclairage ---
        # Éclairage basé sur les heures de lumière de la culture active
        if culture:
            hour = datetime.now().hour
            light_start = 8   # Début éclairage à 8h
            light_end = light_start + int(culture['light_hours_max'])
            should_light = light_start <= hour < light_end

            current_lighting = state['lighting_on']
            if should_light and not current_lighting:
                conn.execute("UPDATE system_state SET lighting_on = 1, updated_at = ? WHERE id = 1",
                             (datetime.now().isoformat(),))
            elif not should_light and current_lighting:
                conn.execute("UPDATE system_state SET lighting_on = 0, updated_at = ? WHERE id = 1",
                             (datetime.now().isoformat(),))

        conn.commit()
        conn.close()
        return alerts

    def _create_alert(self, conn, alert_type, severity, message, value, threshold):
        """
        Créer une alerte si une alerte similaire n'a pas été créée récemment.
        Évite le spam d'alertes en vérifiant les 60 dernières secondes.
        """
        # Vérifier qu'une alerte similaire n'existe pas dans les 60 dernières secondes
        existing = conn.execute('''
            SELECT id FROM alerts 
            WHERE type = ? AND message = ? 
            AND timestamp > datetime('now', '-60 seconds')
        ''', (alert_type, message)).fetchone()

        if existing:
            return None

        cursor = conn.execute('''
            INSERT INTO alerts (type, severity, message, value, threshold)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_type, severity, message, value, threshold))

        return {
            'id': cursor.lastrowid,
            'type': alert_type,
            'severity': severity,
            'message': message,
            'value': value,
            'threshold': threshold,
            'acknowledged': False,
            'timestamp': datetime.now().isoformat()
        }
