"""
HydroNFT - Modèles de données SQLite
Système hydroponique NFT intelligent pour la culture urbaine
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'hydroponic.db')


def get_db():
    """Obtenir une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialiser la base de données avec les tables nécessaires."""
    conn = get_db()
    cursor = conn.cursor()

    # Table des lectures de capteurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ph REAL NOT NULL,
            ec REAL NOT NULL,
            temperature REAL NOT NULL,
            water_level REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table des profils de cultures (Laitue, Basilic, Fraise)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS culture_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            emoji TEXT NOT NULL,
            ph_min REAL NOT NULL,
            ph_max REAL NOT NULL,
            ec_min REAL NOT NULL,
            ec_max REAL NOT NULL,
            temp_min REAL NOT NULL,
            temp_max REAL NOT NULL,
            humidity_min REAL NOT NULL,
            humidity_max REAL NOT NULL,
            light_hours_min REAL NOT NULL,
            light_hours_max REAL NOT NULL,
            nutrients TEXT,
            description TEXT
        )
    ''')

    # Table des alertes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            value REAL,
            threshold TEXT,
            acknowledged INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table de l'état du système
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            pump_on INTEGER DEFAULT 1,
            lighting_on INTEGER DEFAULT 1,
            auto_mode INTEGER DEFAULT 1,
            active_culture_id INTEGER DEFAULT 1,
            ph_threshold_min REAL DEFAULT 5.5,
            ph_threshold_max REAL DEFAULT 6.5,
            ec_threshold_min REAL DEFAULT 0.8,
            ec_threshold_max REAL DEFAULT 2.2,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (active_culture_id) REFERENCES culture_profiles(id)
        )
    ''')

    conn.commit()

    # Insérer les profils de cultures si vides (données du rapport PFE)
    cursor.execute("SELECT COUNT(*) FROM culture_profiles")
    if cursor.fetchone()[0] == 0:
        _insert_default_cultures(cursor)
        conn.commit()

    # Insérer l'état système par défaut
    cursor.execute("SELECT COUNT(*) FROM system_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO system_state (id, pump_on, lighting_on, auto_mode, active_culture_id,
                                       ph_threshold_min, ph_threshold_max, ec_threshold_min, ec_threshold_max)
            VALUES (1, 1, 1, 1, 1, 5.5, 6.5, 0.8, 1.4)
        ''')
        conn.commit()

    conn.close()


def _insert_default_cultures(cursor):
    """
    Insérer les 3 cultures du rapport PFE avec leurs paramètres optimaux.
    Données tirées des Tableaux 1-6 du rapport.
    """
    cultures = [
        {
            'name': 'Laitue',
            'emoji': '🥬',
            'ph_min': 5.5, 'ph_max': 6.5,
            'ec_min': 0.8, 'ec_max': 1.4,
            'temp_min': 18.0, 'temp_max': 22.0,
            'humidity_min': 50.0, 'humidity_max': 70.0,
            'light_hours_min': 10.0, 'light_hours_max': 14.0,
            'nutrients': 'Nitrate de calcium: 685 mg/L, Nitrate de potassium: 550 mg/L, '
                         'Sulfate de calcium: 78 mg/L, Sulfate d\'ammonium: 237 mg/L, '
                         'Sulfate de magnésium: 537 mg/L, Phosphate monocalcique: 589 mg/L',
            'description': 'Le système NFT est idéal pour la culture de la laitue. '
                           'Il permet d\'obtenir des résultats exceptionnels à condition '
                           'd\'utiliser correctement l\'eau et les nutriments.'
        },
        {
            'name': 'Basilic',
            'emoji': '🌿',
            'ph_min': 5.5, 'ph_max': 6.5,
            'ec_min': 1.2, 'ec_max': 1.6,
            'temp_min': 18.0, 'temp_max': 24.0,
            'humidity_min': 40.0, 'humidity_max': 60.0,
            'light_hours_min': 12.0, 'light_hours_max': 16.0,
            'nutrients': 'Phosphore: 46.5 mg/L, Potassium: 175.5 mg/L, '
                         'Calcium: 260 mg/L, Soufre: 80 mg/L, Magnésium: 48.6 mg/L',
            'description': 'Les herbes aromatiques (menthe, coriandre, persil) sont adaptées '
                           'au système NFT, elles bénéficient d\'un accès constant aux nutriments.'
        },
        {
            'name': 'Fraise',
            'emoji': '🍓',
            'ph_min': 5.5, 'ph_max': 6.5,
            'ec_min': 1.8, 'ec_max': 2.2,
            'temp_min': 18.0, 'temp_max': 24.0,
            'humidity_min': 60.0, 'humidity_max': 75.0,
            'light_hours_min': 12.0, 'light_hours_max': 14.0,
            'nutrients': 'Azote: 160-170 mg/L, Phosphore: 55-60 mg/L, '
                         'Potassium: 400-500 mg/L, Rapport K:Ca = 1.4:1, Rapport K:Mg = 4:1',
            'description': 'Le système NFT permet une gestion précise de la nutrition et '
                           'de l\'irrigation, c\'est pourquoi il est fréquemment utilisé dans '
                           'la culture de la fraise.'
        }
    ]

    for c in cultures:
        cursor.execute('''
            INSERT INTO culture_profiles
            (name, emoji, ph_min, ph_max, ec_min, ec_max, temp_min, temp_max,
             humidity_min, humidity_max, light_hours_min, light_hours_max, nutrients, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (c['name'], c['emoji'], c['ph_min'], c['ph_max'], c['ec_min'], c['ec_max'],
              c['temp_min'], c['temp_max'], c['humidity_min'], c['humidity_max'],
              c['light_hours_min'], c['light_hours_max'], c['nutrients'], c['description']))


if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!")
