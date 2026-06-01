# -*- coding: utf-8 -*-
"""
Capture des screenshots reels de l'application HydroNFT
avec Playwright (Chrome headless en mode mobile)
"""

from playwright.sync_api import sync_playwright
import time
import os

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BASE_URL = "http://localhost:3000"


def capture_all():
    print("=== Capture des screenshots HydroNFT ===")
    print(f"Dossier: {SCREENSHOT_DIR}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Creer un contexte mobile iPhone 12
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
            is_mobile=True,
        )
        page = context.new_page()

        # 1. SPLASH SCREEN
        print("1. Splash Screen...")
        page.goto(BASE_URL)
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_splash_screen.png"))
        print("   -> 01_splash_screen.png")

        # 2. DASHBOARD - attendre que le splash disparaisse et les donnees chargent
        print("2. Dashboard...")
        page.wait_for_timeout(5000)  # splash 1.5s + chargement donnees
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_dashboard.png"))
        print("   -> 02_dashboard.png")

        # 3. CONTROLE
        print("3. Controle Systeme...")
        page.evaluate("navigateTo('control')")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_controle.png"))
        print("   -> 03_controle.png")

        # 4. CULTURES
        print("4. Cultures...")
        page.evaluate("navigateTo('cultures')")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_cultures.png"))
        print("   -> 04_cultures.png")

        # 5. HISTORIQUE (pH)
        print("5. Historique (pH)...")
        page.evaluate("navigateTo('history')")
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_historique_ph.png"))
        print("   -> 05_historique_ph.png")

        # 6. HISTORIQUE (EC)
        print("6. Historique (EC)...")
        page.evaluate("activeChartTab='ec'; loadHistory()")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_historique_ec.png"))
        print("   -> 06_historique_ec.png")

        # 7. HISTORIQUE (Temperature)
        print("7. Historique (Temperature)...")
        page.evaluate("activeChartTab='temperature'; loadHistory()")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_historique_temp.png"))
        print("   -> 07_historique_temp.png")

        # 8. ALERTES
        print("8. Alertes...")
        page.evaluate("navigateTo('alerts')")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_alertes.png"))
        print("   -> 08_alertes.png")

        # 9. CONTROLE - Mode Manuel
        print("9. Controle (mode manuel)...")
        page.evaluate("navigateTo('control')")
        page.wait_for_timeout(2000)
        page.evaluate("setMode(false)")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_controle_manuel.png"))
        print("   -> 09_controle_manuel.png")

        # Remettre en auto
        page.evaluate("setMode(true)")
        page.wait_for_timeout(1000)

        # 10. DASHBOARD vue finale
        print("10. Dashboard (vue finale)...")
        page.evaluate("navigateTo('dashboard')")
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_dashboard_final.png"))
        print("   -> 10_dashboard_final.png")

        browser.close()

    print()
    print(f"=== Termine ! ===")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.endswith('.png'):
            size = os.path.getsize(os.path.join(SCREENSHOT_DIR, f))
            print(f"  {f} ({size//1024} KB)")


if __name__ == "__main__":
    capture_all()
