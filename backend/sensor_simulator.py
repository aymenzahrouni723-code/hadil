"""
HydroNFT - Simulateur de capteurs ESP32
Simule les données des capteurs pH, EC, Température et Niveau d'eau
avec des variations réalistes basées sur les spécifications du rapport PFE.
"""

import random
import threading
import time
from datetime import datetime
from models import get_db


class SensorSimulator:
    """
    Simule les capteurs connectés à l'ESP32:
    - Capteur pH (plage: 0-14, optimal: 5.5-6.5)
    - Capteur EC DFR0300 (plage: 0-20 mS/cm)
    - Capteur température DS18B20 (plage: -55 à +125°C)
    - Capteur niveau d'eau ST045 (sortie: 400-700)
    """

    def __init__(self):
        # Valeurs initiales réalistes
        self.current_ph = 6.1
        self.current_ec = 1.3
        self.current_temperature = 21.0
        self.current_water_level = 85.0  # en pourcentage

        # Thread de simulation
        self._running = False
        self._thread = None
        self._interval = 5  # secondes entre chaque lecture

    def start(self):
        """Démarrer la simulation des capteurs."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._simulate_loop, daemon=True)
        self._thread.start()
        print("[SIMULATEUR] Capteurs ESP32 demarres (intervalle: {}s)".format(self._interval))

    def stop(self):
        """Arrêter la simulation."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        print("[SIMULATEUR] Capteurs ESP32 arretes")

    def _simulate_loop(self):
        """Boucle principale de simulation."""
        while self._running:
            self._update_sensors()
            self._save_reading()
            time.sleep(self._interval)

    def _update_sensors(self):
        """
        Mettre à jour les valeurs des capteurs avec des variations réalistes.
        Les capteurs physiques ont des fluctuations naturelles.
        """
        # pH: oscille autour de la valeur courante avec dérive lente
        # Capteur pH analogique (0-14), précision typique ±0.1
        drift = random.gauss(0, 0.05)
        noise = random.gauss(0, 0.02)
        self.current_ph += drift + noise
        # Limiter à la plage réaliste (légèrement élargie pour créer des alertes)
        self.current_ph = max(4.5, min(8.0, self.current_ph))
        # Tendance de retour vers la zone optimale (le système corrige)
        if self.current_ph < 5.5:
            self.current_ph += random.uniform(0.01, 0.05)
        elif self.current_ph > 6.5:
            self.current_ph -= random.uniform(0.01, 0.05)

        # EC: conductivité électrique (DFR0300, plage 0-20 mS/cm, précision ±5%)
        drift = random.gauss(0, 0.03)
        self.current_ec += drift
        self.current_ec = max(0.3, min(5.0, self.current_ec))
        # Retour vers la plage optimale
        if self.current_ec < 0.8:
            self.current_ec += random.uniform(0.01, 0.03)
        elif self.current_ec > 2.2:
            self.current_ec -= random.uniform(0.01, 0.03)

        # Température: DS18B20 (précision ±0.2°C)
        # Varie selon l'heure (plus chaud le jour, plus frais la nuit)
        hour = datetime.now().hour
        if 8 <= hour <= 20:  # Jour
            target_temp = random.uniform(20.0, 24.0)
        else:  # Nuit
            target_temp = random.uniform(14.0, 18.0)

        # Approche progressive de la température cible
        diff = target_temp - self.current_temperature
        self.current_temperature += diff * 0.05 + random.gauss(0, 0.1)
        self.current_temperature = max(5.0, min(40.0, self.current_temperature))

        # Niveau d'eau: ST045 (400-700 → converti en pourcentage 0-100%)
        # Le niveau descend naturellement (les plantes consomment l'eau)
        self.current_water_level -= random.uniform(0.01, 0.1)
        # Remplissage automatique quand le niveau est trop bas
        if self.current_water_level < 20:
            self.current_water_level = random.uniform(85, 95)
        self.current_water_level = max(0, min(100, self.current_water_level))

    def _save_reading(self):
        """Sauvegarder la lecture courante en base de données."""
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO sensor_readings (ph, ec, temperature, water_level)
                VALUES (?, ?, ?, ?)
            ''', (
                round(self.current_ph, 2),
                round(self.current_ec, 2),
                round(self.current_temperature, 1),
                round(self.current_water_level, 1)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SIMULATEUR] Erreur sauvegarde: {e}")

    def get_current_values(self):
        """Retourner les valeurs courantes des capteurs."""
        return {
            'ph': round(self.current_ph, 2),
            'ec': round(self.current_ec, 2),
            'temperature': round(self.current_temperature, 1),
            'water_level': round(self.current_water_level, 1),
            'timestamp': datetime.now().isoformat()
        }
