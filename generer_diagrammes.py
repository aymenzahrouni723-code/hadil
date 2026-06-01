# -*- coding: utf-8 -*-
"""
Generation des diagrammes UML et techniques pour le Chapitre 5
du rapport PFE HydroNFT - Hadil BOUDHRIOUWA
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

DIAGRAM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrammes")
os.makedirs(DIAGRAM_DIR, exist_ok=True)

# Couleurs du design system HydroNFT
C = {
    'bg': '#0F1923', 'card': '#1A2332', 'border': '#2A3A4A',
    'green': '#2ECC71', 'blue': '#3498DB', 'teal': '#1ABC9C',
    'orange': '#E67E22', 'red': '#E74C3C', 'yellow': '#F39C12',
    'white': '#F8FAFC', 'gray': '#94A3B8', 'dark_gray': '#64748B',
    'purple': '#9B59B6', 'light_bg': '#FFFFFF', 'light_card': '#F0F4F8',
}


def save(fig, name):
    path = os.path.join(DIAGRAM_DIR, f"{name}.png")
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [OK] {name}.png")
    return path


# ════════════════════════════════════════════════════════
# 1. DIAGRAMME DE CAS D'UTILISATION
# ════════════════════════════════════════════════════════
def diag_use_case():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.5)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Titre
    ax.text(5, 8.2, "Diagramme de cas d'utilisation - Application HydroNFT",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    # Acteur
    ax.plot(1.0, 4.5, 'o', markersize=18, color=C['blue'], zorder=5)
    ax.plot([1.0, 1.0], [3.5, 4.2], color=C['blue'], linewidth=2.5)
    ax.plot([0.6, 1.4], [4.0, 4.0], color=C['blue'], linewidth=2.5)
    ax.plot([0.7, 1.0], [3.0, 3.5], color=C['blue'], linewidth=2.5)
    ax.plot([1.3, 1.0], [3.0, 3.5], color=C['blue'], linewidth=2.5)
    ax.text(1.0, 2.6, 'Utilisateur', ha='center', fontsize=10, fontweight='bold', color=C['blue'])

    # Systeme boundary
    rect = FancyBboxPatch((2.8, 0.3), 6.5, 7.8, boxstyle="round,pad=0.15",
                           facecolor='#F8FBFF', edgecolor=C['blue'], linewidth=2, linestyle='--')
    ax.add_patch(rect)
    ax.text(6.05, 7.85, 'Application HydroNFT', ha='center', fontsize=11,
            fontweight='bold', color=C['blue'], style='italic')

    # Cas d'utilisation (ellipses)
    cases = [
        (5.8, 7.0, "Consulter le\ntableau de bord"),
        (5.8, 6.0, "Visualiser les donnees\ndes capteurs en temps reel"),
        (5.8, 5.0, "Consulter l'historique\ndes mesures"),
        (5.8, 4.0, "Demarrer / Arreter\nla pompe"),
        (5.8, 3.0, "Controler\nl'eclairage LED"),
        (5.8, 2.0, "Selectionner\nune culture"),
        (5.8, 1.0, "Consulter et acquitter\nles alertes"),
    ]

    colors_uc = [C['green'], C['teal'], C['blue'], C['orange'], C['yellow'], C['purple'], C['red']]

    for i, (x, y, text) in enumerate(cases):
        ellipse = mpatches.Ellipse((x, y), 3.8, 0.75, facecolor=colors_uc[i] + '18',
                                    edgecolor=colors_uc[i], linewidth=1.5)
        ax.add_patch(ellipse)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='500', color='#1a1a2e')
        # Ligne vers acteur
        ax.annotate('', xy=(x - 1.9, y), xytext=(1.5, 4.0),
                    arrowprops=dict(arrowstyle='-', color=C['dark_gray'], lw=1, linestyle='-'))

    # Acteur secondaire : ESP32
    ax.plot(9.8, 4.5, 's', markersize=16, color=C['green'], zorder=5)
    ax.text(9.8, 4.0, 'ESP32', ha='center', fontsize=9, fontweight='bold', color=C['green'])

    # Lignes ESP32
    for y in [7.0, 6.0, 5.0]:
        ax.annotate('', xy=(7.7, y), xytext=(9.5, 4.5),
                    arrowprops=dict(arrowstyle='-', color=C['green'], lw=0.8, linestyle='--'))

    return save(fig, "01_use_case")


# ════════════════════════════════════════════════════════
# 2. DIAGRAMME DE SEQUENCE - MONITORING
# ════════════════════════════════════════════════════════
def diag_sequence_monitoring():
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(5.5, 9.7, "Diagramme de sequence - Monitoring des capteurs en temps reel",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    # Acteurs / Objets
    actors = [
        (1.5, "Utilisateur", C['blue']),
        (4.0, "Application\n(Frontend)", C['green']),
        (6.5, "Serveur\n(API REST)", C['orange']),
        (9.0, "Base de\ndonnees SQLite", C['purple']),
    ]

    for x, label, color in actors:
        box = FancyBboxPatch((x - 0.7, 8.8), 1.4, 0.7, boxstyle="round,pad=0.08",
                              facecolor=color + '20', edgecolor=color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, 9.15, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1a1a2e')
        # Ligne de vie
        ax.plot([x, x], [1.0, 8.8], color=color, linewidth=1, linestyle='--', alpha=0.5)

    # Messages
    msgs = [
        (8.2, 1.5, 4.0, "Ouvre le Dashboard", C['blue'], False),
        (7.5, 4.0, 6.5, "GET /api/sensors/current", C['green'], False),
        (6.8, 6.5, 9.0, "SELECT * FROM sensor_readings", C['orange'], False),
        (6.1, 9.0, 6.5, "Donnees capteurs (JSON)", C['purple'], True),
        (5.4, 6.5, 4.0, "{ sensors: {pH, EC, temp, water}, system: {...} }", C['orange'], True),
        (4.7, 4.0, 1.5, "Affiche les 4 jauges SVG", C['green'], True),
        (3.8, 4.0, 6.5, "[loop] toutes les 3 secondes", C['dark_gray'], False),
        (3.1, 6.5, 4.0, "Nouvelles valeurs capteurs", C['orange'], True),
        (2.4, 4.0, 1.5, "Met a jour les jauges", C['green'], True),
    ]

    for y, x1, x2, text, color, dashed in msgs:
        style = '--' if dashed else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5, linestyle=style))
        mid = (x1 + x2) / 2
        offset = 0.15
        ax.text(mid, y + offset, text, ha='center', fontsize=7.5,
                color=color, fontweight='500',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.9))

    # Loop box
    loop_rect = FancyBboxPatch((3.3, 2.0), 4.0, 2.2, boxstyle="round,pad=0.05",
                                facecolor='#F0F8FF', edgecolor=C['blue'], linewidth=1, linestyle='--')
    ax.add_patch(loop_rect)
    ax.text(3.5, 4.05, 'loop [3s]', fontsize=7, fontweight='bold', color=C['blue'],
            bbox=dict(boxstyle='round,pad=0.1', facecolor=C['blue'] + '20', edgecolor=C['blue']))

    return save(fig, "02_sequence_monitoring")


# ════════════════════════════════════════════════════════
# 3. DIAGRAMME DE SEQUENCE - CONTROLE POMPE
# ════════════════════════════════════════════════════════
def diag_sequence_control():
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(5.5, 9.7, "Diagramme de sequence - Controle a distance de la pompe",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    actors = [
        (1.5, "Utilisateur", C['blue']),
        (4.0, "Application\n(Frontend)", C['green']),
        (6.5, "Serveur\n(API REST)", C['orange']),
        (9.0, "ESP32 +\nPompe", C['red']),
    ]

    for x, label, color in actors:
        box = FancyBboxPatch((x - 0.7, 8.8), 1.4, 0.7, boxstyle="round,pad=0.08",
                              facecolor=color + '20', edgecolor=color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, 9.15, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1a1a2e')
        ax.plot([x, x], [1.0, 8.8], color=color, linewidth=1, linestyle='--', alpha=0.5)

    msgs = [
        (8.0, 1.5, 4.0, "Appuie sur toggle Pompe", C['blue'], False),
        (7.2, 4.0, 6.5, "POST /api/pump/toggle", C['green'], False),
        (6.4, 6.5, 6.5, "UPDATE system_state\nSET pump_on = 0/1", C['orange'], False),
        (5.6, 6.5, 9.0, "Envoie commande ON/OFF", C['orange'], False),
        (4.8, 9.0, 6.5, "Confirmation execution", C['red'], True),
        (4.0, 6.5, 4.0, "{ pump_on: true/false }", C['orange'], True),
        (3.2, 4.0, 1.5, "Met a jour le toggle switch\n(vert = ON, gris = OFF)", C['green'], True),
        (2.2, 4.0, 6.5, "GET /api/system/status\n(verification)", C['green'], False),
        (1.4, 6.5, 4.0, "Etat confirme du systeme", C['orange'], True),
    ]

    for y, x1, x2, text, color, dashed in msgs:
        style = '--' if dashed else '-'
        if x1 == x2:  # Self message
            ax.annotate('', xy=(x1 + 0.8, y - 0.2), xytext=(x1, y),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                                       connectionstyle="arc3,rad=-0.3"))
            ax.text(x1 + 1.2, y - 0.1, text, fontsize=7, color=color, fontweight='500')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5, linestyle=style))
            mid = (x1 + x2) / 2
            ax.text(mid, y + 0.15, text, ha='center', fontsize=7.5, color=color, fontweight='500',
                    bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.9))

    return save(fig, "03_sequence_controle")


# ════════════════════════════════════════════════════════
# 4. SCHEMA BASE DE DONNEES
# ════════════════════════════════════════════════════════
def diag_database():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(6, 7.2, "Schema de la base de donnees SQLite - HydroNFT",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    def draw_table(ax, x, y, name, columns, color, pk_count=1):
        w, row_h = 2.8, 0.28
        h = (len(columns) + 1) * row_h + 0.1

        # Header
        header = FancyBboxPatch((x, y - row_h - 0.05), w, row_h + 0.1,
                                 boxstyle="round,pad=0.05", facecolor=color, edgecolor=color, linewidth=1.5)
        ax.add_patch(header)
        ax.text(x + w/2, y - row_h/2 + 0.02, name, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='white')

        # Body
        body = FancyBboxPatch((x, y - h), w, h - row_h - 0.05,
                               boxstyle="round,pad=0.05", facecolor='#FAFBFC',
                               edgecolor=color, linewidth=1.2)
        ax.add_patch(body)

        for i, col in enumerate(columns):
            cy = y - (i + 1.5) * row_h - 0.05
            prefix = "PK " if i < pk_count else "   "
            style = 'bold' if i < pk_count else 'normal'
            col_color = color if i < pk_count else '#333333'
            ax.text(x + 0.15, cy, f"{prefix}{col}", va='center', fontsize=7.5,
                    fontweight=style, color=col_color, family='monospace')

        return y - h

    # Table 1: sensor_readings
    draw_table(ax, 0.3, 6.5, "sensor_readings", [
        "id INTEGER", "ph REAL", "ec REAL",
        "temperature REAL", "water_level REAL", "timestamp DATETIME"
    ], C['green'])

    # Table 2: culture_profiles
    draw_table(ax, 3.6, 6.5, "culture_profiles", [
        "id INTEGER", "name TEXT", "emoji TEXT",
        "ph_min REAL", "ph_max REAL", "ec_min REAL", "ec_max REAL",
        "temp_min REAL", "temp_max REAL",
        "humidity_min REAL", "humidity_max REAL",
        "light_hours_min REAL", "light_hours_max REAL",
        "nutrients TEXT", "description TEXT"
    ], C['blue'])

    # Table 3: system_state
    draw_table(ax, 6.9, 6.5, "system_state", [
        "id INTEGER (=1)", "pump_on INTEGER", "lighting_on INTEGER",
        "auto_mode INTEGER", "active_culture_id FK",
        "ph_threshold_min REAL", "ph_threshold_max REAL",
        "ec_threshold_min REAL", "ec_threshold_max REAL",
        "updated_at DATETIME"
    ], C['orange'])

    # Table 4: alerts
    draw_table(ax, 10.0, 6.5, "alerts", [
        "id INTEGER", "type TEXT", "severity TEXT",
        "message TEXT", "value REAL", "threshold TEXT",
        "acknowledged INTEGER", "timestamp DATETIME"
    ], C['red'])

    # Relation: system_state -> culture_profiles (FK)
    ax.annotate('', xy=(6.4, 3.8), xytext=(6.9, 4.3),
                arrowprops=dict(arrowstyle='->', color=C['purple'], lw=2,
                               connectionstyle="arc3,rad=0.2"))
    ax.text(6.3, 3.5, "FK: active_culture_id", fontsize=7, color=C['purple'],
            fontweight='bold', style='italic')

    return save(fig, "04_database_schema")


# ════════════════════════════════════════════════════════
# 5. DIAGRAMME DE NAVIGATION
# ════════════════════════════════════════════════════════
def diag_navigation():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(5, 7.2, "Diagramme de navigation entre les ecrans",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    # Splash
    splash = FancyBboxPatch((3.8, 5.8), 2.4, 0.9, boxstyle="round,pad=0.1",
                             facecolor=C['green'] + '15', edgecolor=C['green'], linewidth=2)
    ax.add_patch(splash)
    ax.text(5, 6.25, "Splash Screen\n(1.5s)", ha='center', va='center',
            fontsize=9, fontweight='bold', color=C['green'])

    # Arrow splash -> dashboard
    ax.annotate('', xy=(5, 5.3), xytext=(5, 5.8),
                arrowprops=dict(arrowstyle='->', color=C['green'], lw=2))

    # 5 ecrans en arc
    screens = [
        (1.2, 4.2, "Dashboard\n(Jauges + Statuts)", C['green'], "3s refresh"),
        (3.5, 4.2, "Controle\n(Pompe + LED)", C['orange'], "3s refresh"),
        (5.8, 4.2, "Cultures\n(Laitue/Basilic/Fraise)", C['purple'], "on demand"),
        (8.2, 4.2, "Historique\n(Graphiques)", C['blue'], "10s refresh"),
        (5.0, 2.0, "Alertes\n(Notifications)", C['red'], "5s refresh"),
    ]

    for x, y, label, color, refresh in screens:
        box = FancyBboxPatch((x - 1.1, y - 0.5), 2.2, 1.0, boxstyle="round,pad=0.1",
                              facecolor=color + '12', edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y + 0.05, label, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='#1a1a2e')
        ax.text(x, y - 0.35, refresh, ha='center', fontsize=6.5, color=C['dark_gray'], style='italic')

    # Navbar label
    navbar = FancyBboxPatch((0.5, 0.6), 9.0, 0.6, boxstyle="round,pad=0.08",
                             facecolor='#1a1a2e', edgecolor=C['dark_gray'], linewidth=1.5)
    ax.add_patch(navbar)
    ax.text(5, 0.9, "Barre de Navigation (Bottom Navbar) — Navigation entre tous les ecrans",
            ha='center', va='center', fontsize=9, fontweight='bold', color='white')

    # Arrows from navbar to each screen
    for x, y, _, color, _ in screens:
        ax.annotate('', xy=(x, y - 0.5), xytext=(x, 1.2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2,
                                   linestyle='--', alpha=0.6))

    return save(fig, "05_navigation")


# ════════════════════════════════════════════════════════
# 6. ARCHITECTURE DE DEPLOIEMENT
# ════════════════════════════════════════════════════════
def diag_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(5.5, 7.2, "Architecture de deploiement du systeme HydroNFT",
            ha='center', fontsize=13, fontweight='bold', color='#1a1a2e')

    # ESP32 + Capteurs (gauche)
    esp_box = FancyBboxPatch((0.3, 2.5), 2.5, 4.0, boxstyle="round,pad=0.15",
                              facecolor=C['green'] + '10', edgecolor=C['green'], linewidth=2)
    ax.add_patch(esp_box)
    ax.text(1.55, 6.2, "Systeme Physique", ha='center', fontsize=10,
            fontweight='bold', color=C['green'])

    # ESP32
    esp = FancyBboxPatch((0.6, 4.3), 1.9, 0.7, boxstyle="round,pad=0.08",
                          facecolor=C['green'] + '30', edgecolor=C['green'], linewidth=1.5)
    ax.add_patch(esp)
    ax.text(1.55, 4.65, "ESP32\n(Microcontroleur)", ha='center', va='center',
            fontsize=8, fontweight='bold', color='#1a1a2e')

    # Capteurs
    capteurs = ["pH (BNC)", "EC (DFR0300)", "Temp (DS18B20)", "Niveau (ST045)"]
    for i, cap in enumerate(capteurs):
        y = 3.9 - i * 0.35
        ax.text(1.55, y, f"  {cap}", ha='center', fontsize=7, color=C['dark_gray'])

    # Actionneurs
    ax.text(1.55, 2.7, "Pompe 600L/H | LED", ha='center', fontsize=7.5,
            fontweight='bold', color=C['orange'])

    # Wi-Fi arrow
    ax.annotate('Wi-Fi\n2.4 GHz', xy=(3.5, 4.5), xytext=(2.8, 4.5),
                fontsize=8, fontweight='bold', color=C['blue'], ha='center',
                arrowprops=dict(arrowstyle='<->', color=C['blue'], lw=2.5))

    # Serveur (milieu)
    srv_box = FancyBboxPatch((3.8, 2.5), 3.0, 4.0, boxstyle="round,pad=0.15",
                              facecolor=C['orange'] + '10', edgecolor=C['orange'], linewidth=2)
    ax.add_patch(srv_box)
    ax.text(5.3, 6.2, "Serveur (Render.com)", ha='center', fontsize=10,
            fontweight='bold', color=C['orange'])

    components = [
        (5.3, 5.4, "Node.js + Express", C['green']),
        (5.3, 4.6, "API REST (12 endpoints)", C['blue']),
        (5.3, 3.8, "Simulateur ESP32", C['teal']),
        (5.3, 3.0, "SQLite (sql.js)", C['purple']),
    ]
    for x, y, label, color in components:
        comp = FancyBboxPatch((x - 1.2, y - 0.25), 2.4, 0.5, boxstyle="round,pad=0.06",
                               facecolor=color + '15', edgecolor=color, linewidth=1)
        ax.add_patch(comp)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#1a1a2e')

    # HTTP arrow
    ax.annotate('HTTP/HTTPS\nAPI REST', xy=(7.5, 4.5), xytext=(6.8, 4.5),
                fontsize=8, fontweight='bold', color=C['blue'], ha='center',
                arrowprops=dict(arrowstyle='<->', color=C['blue'], lw=2.5))

    # Client (droite)
    cli_box = FancyBboxPatch((7.8, 2.5), 2.8, 4.0, boxstyle="round,pad=0.15",
                              facecolor=C['blue'] + '10', edgecolor=C['blue'], linewidth=2)
    ax.add_patch(cli_box)
    ax.text(9.2, 6.2, "Client (Navigateur)", ha='center', fontsize=10,
            fontweight='bold', color=C['blue'])

    cli_components = [
        (9.2, 5.3, "HTML5 + CSS3 + JS", '#333333'),
        (9.2, 4.5, "Jauges SVG", C['green']),
        (9.2, 3.7, "Chart.js (graphiques)", C['orange']),
        (9.2, 2.9, "Navigation SPA", C['teal']),
    ]
    for x, y, label, color in cli_components:
        comp = FancyBboxPatch((x - 1.1, y - 0.25), 2.2, 0.5, boxstyle="round,pad=0.06",
                               facecolor=color + '15', edgecolor=color, linewidth=1)
        ax.add_patch(comp)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#1a1a2e')

    # Devices at bottom
    devices = ["Smartphone", "Tablette", "PC"]
    for i, d in enumerate(devices):
        x = 8.4 + i * 0.9
        ax.text(x, 2.0, d, ha='center', fontsize=7, color=C['dark_gray'],
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#F0F0F0', edgecolor=C['dark_gray'], lw=0.5))

    return save(fig, "06_architecture")


# ════════════════════════════════════════════════════════
# 7. DIAGRAMME D'ACTIVITE - CONTROLE AUTOMATIQUE
# ════════════════════════════════════════════════════════
def diag_activity():
    fig, ax = plt.subplots(1, 1, figsize=(8, 12))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 13)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(4, 12.7, "Diagramme d'activite - Logique de controle automatique",
            ha='center', fontsize=12, fontweight='bold', color='#1a1a2e')

    def act_box(x, y, text, color, w=3.0, h=0.55):
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1",
                              facecolor=color + '18', edgecolor=color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=8, fontweight='bold', color='#1a1a2e')

    def diamond(x, y, text, color):
        d = 0.35
        pts = np.array([[x, y+d], [x+d*1.5, y], [x, y-d], [x-d*1.5, y]])
        poly = plt.Polygon(pts, facecolor=color + '18', edgecolor=color, linewidth=1.5)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=7, fontweight='bold', color='#1a1a2e')

    def arrow(x1, y1, x2, y2, label="", color='#333'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx + 0.15, my, label, fontsize=7, color=color, fontweight='bold')

    # Start
    ax.plot(4, 12.3, 'o', markersize=15, color='#1a1a2e', zorder=5)
    ax.text(4, 12.3, '', ha='center')
    arrow(4, 12.15, 4, 11.8, color='#333')

    # Lecture capteurs
    act_box(4, 11.5, "Lire les capteurs ESP32\n(pH, EC, Temp, Niveau)", C['green'])
    arrow(4, 11.2, 4, 10.8, color='#333')

    # Mode auto?
    diamond(4, 10.5, "Mode\nAuto?", C['blue'])
    arrow(4, 10.15, 4, 9.7, "Oui", C['green'])
    ax.annotate('', xy=(7, 10.5), xytext=(5.5, 10.5),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5))
    ax.text(6.0, 10.65, "Non", fontsize=7, fontweight='bold', color=C['red'])
    act_box(7, 10.5, "Pas\nd'action", C['dark_gray'], w=1.2, h=0.5)

    # pH OK?
    diamond(4, 9.4, "pH dans\nplage?", C['green'])
    arrow(4, 9.05, 4, 8.6, "Oui", C['green'])

    ax.annotate('', xy=(1.5, 9.4), xytext=(2.5, 9.4),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5))
    ax.text(2.2, 9.55, "Non", fontsize=7, fontweight='bold', color=C['red'])
    act_box(1.2, 9.4, "Alerte pH\nArret pompe", C['red'], w=1.8, h=0.5)

    # EC OK?
    diamond(4, 8.3, "EC dans\nplage?", C['blue'])
    arrow(4, 7.95, 4, 7.5, "Oui", C['green'])

    ax.annotate('', xy=(1.5, 8.3), xytext=(2.5, 8.3),
                arrowprops=dict(arrowstyle='->', color=C['red'], lw=1.5))
    ax.text(2.2, 8.45, "Non", fontsize=7, fontweight='bold', color=C['red'])
    act_box(1.2, 8.3, "Alerte EC\nArret pompe", C['red'], w=1.8, h=0.5)

    # Niveau eau?
    diamond(4, 7.2, "Niveau\n> 25%?", C['teal'])
    arrow(4, 6.85, 4, 6.4, "Oui", C['green'])

    ax.annotate('', xy=(6.5, 7.2), xytext=(5.5, 7.2),
                arrowprops=dict(arrowstyle='->', color=C['yellow'], lw=1.5))
    ax.text(5.6, 7.35, "Non", fontsize=7, fontweight='bold', color=C['yellow'])
    act_box(7, 7.2, "Alerte\nniveau bas", C['yellow'], w=1.5, h=0.5)

    # Temperature?
    diamond(4, 6.1, "Temp.\nOK?", C['orange'])
    arrow(4, 5.75, 4, 5.3, "Oui", C['green'])

    ax.annotate('', xy=(6.5, 6.1), xytext=(5.5, 6.1),
                arrowprops=dict(arrowstyle='->', color=C['yellow'], lw=1.5))
    ax.text(5.6, 6.25, "Non", fontsize=7, fontweight='bold', color=C['yellow'])
    act_box(7, 6.1, "Alerte\ntemperature", C['yellow'], w=1.5, h=0.5)

    # Pompe ON
    act_box(4, 5.0, "Pompe ON\n(parametres normaux)", C['green'])
    arrow(4, 4.7, 4, 4.3, color='#333')

    # Eclairage
    diamond(4, 4.0, "Heure\nlumiere?", C['yellow'])
    arrow(4, 3.65, 4, 3.2, color='#333')

    ax.annotate('', xy=(6.5, 4.0), xytext=(5.5, 4.0),
                arrowprops=dict(arrowstyle='->', color=C['yellow'], lw=1.5))
    act_box(7, 4.0, "LED ON", C['yellow'], w=1.2, h=0.4)

    ax.annotate('', xy=(1.5, 4.0), xytext=(2.5, 4.0),
                arrowprops=dict(arrowstyle='->', color=C['dark_gray'], lw=1.5))
    act_box(1.2, 4.0, "LED OFF", C['dark_gray'], w=1.2, h=0.4)

    # Sauvegarder
    act_box(4, 2.9, "Sauvegarder en base de donnees", C['purple'])
    arrow(4, 2.6, 4, 2.2, color='#333')

    # Attendre
    act_box(4, 1.9, "Attendre 5 secondes", C['dark_gray'])
    arrow(4, 1.6, 4, 1.2, color='#333')

    # Loop back
    ax.annotate('', xy=(0.5, 12.0), xytext=(0.5, 1.2),
                arrowprops=dict(arrowstyle='->', color=C['blue'], lw=1.5,
                               connectionstyle="arc3,rad=0"))
    ax.annotate('', xy=(4, 12.0), xytext=(0.5, 12.0),
                arrowprops=dict(arrowstyle='->', color=C['blue'], lw=1.5))
    ax.text(0.3, 6.5, "Boucle\ninfinie", fontsize=7, fontweight='bold', color=C['blue'],
            rotation=90, ha='center')

    return save(fig, "07_activite_controle")


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════
def main():
    print("=== Generation des diagrammes HydroNFT ===")
    print()

    print("1. Diagramme de cas d'utilisation...")
    diag_use_case()

    print("2. Diagramme de sequence - Monitoring...")
    diag_sequence_monitoring()

    print("3. Diagramme de sequence - Controle pompe...")
    diag_sequence_control()

    print("4. Schema base de donnees...")
    diag_database()

    print("5. Diagramme de navigation...")
    diag_navigation()

    print("6. Architecture de deploiement...")
    diag_architecture()

    print("7. Diagramme d'activite - Controle auto...")
    diag_activity()

    print()
    print(f"=== 7 diagrammes generes dans {DIAGRAM_DIR} ===")
    for f in sorted(os.listdir(DIAGRAM_DIR)):
        if f.endswith('.png'):
            size = os.path.getsize(os.path.join(DIAGRAM_DIR, f))
            print(f"  {f} ({size//1024} KB)")


if __name__ == "__main__":
    main()
