#!/usr/bin/env python3
"""
Script de prueba para verificar que Selenium y ChromeDriver funcionan correctamente
"""

import sys

print("=" * 70)
print("TEST DE SELENIUM PARA LINKEDIN AUTOMATOR")
print("=" * 70)

# 1. Verificar imports
print("\n[1/5] Verificando imports...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    print("✓ Selenium y webdriver-manager disponibles")
except ImportError as e:
    print(f"✗ Error: {e}")
    print("→ Ejecuta: pip install selenium webdriver-manager")
    sys.exit(1)

# 2. Verificar Chrome/Chromium
print("\n[2/5] Verificando navegador Chrome/Chromium...")
import shutil
import subprocess

chrome_binary = None
for cmd in ['chromium-browser', 'google-chrome', 'chromium', 'google-chrome-stable']:
    if shutil.which(cmd):
        chrome_binary = cmd
        break

if chrome_binary:
    try:
        version = subprocess.check_output([chrome_binary, '--version'], 
                                         stderr=subprocess.STDOUT, 
                                         text=True).strip()
        print(f"✓ {version}")
    except Exception as e:
        print(f"⚠ Chrome encontrado pero error al obtener versión: {e}")
else:
    print("✗ Chrome/Chromium NO encontrado")
    print("\nINSTALACIÓN REQUERIDA:")
    print("  sudo apt update")
    print("  sudo apt install -y chromium-browser")
    print("\nNo se puede continuar sin Chrome/Chromium.")
    sys.exit(1)

# 3. Inicializar WebDriver
print("\n[3/5] Descargando/verificando ChromeDriver...")
try:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    print("  → Usando webdriver-manager (puede tardar en la primera ejecución)...")
    service = Service(ChromeDriverManager().install())
    print("✓ ChromeDriver descargado/verificado")
    
except Exception as e:
    print(f"✗ Error al descargar ChromeDriver: {e}")
    sys.exit(1)

# 4. Test de inicialización
print("\n[4/5] Iniciando WebDriver...")
try:
    driver = webdriver.Chrome(service=service, options=options)
    print("✓ WebDriver iniciado correctamente")
    
except Exception as e:
    print(f"✗ Error al iniciar WebDriver: {e}")
    sys.exit(1)

# 5. Test de navegación
print("\n[5/5] Probando navegación web...")
try:
    driver.get("https://www.google.com")
    title = driver.title
    print(f"✓ Navegación exitosa: '{title}'")
    
    driver.quit()
    print("✓ WebDriver cerrado correctamente")
    
except Exception as e:
    print(f"✗ Error durante navegación: {e}")
    try:
        driver.quit()
    except:
        pass
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TODOS LOS TESTS PASARON - Selenium está listo para usar")
print("=" * 70)
print("\nPuedes ejecutar la aplicación con:")
print("  source venv/bin/activate")
print("  flask run")
