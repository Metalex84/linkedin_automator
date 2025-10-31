''' 
Copyright (c) 2024 [Alejandro Gonzalez Venegas]

Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
https://creativecommons.org/licenses/by-nc/4.0/
'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import shutil


def get_chrome_driver():
    """
    Inicializa y retorna un WebDriver de Chrome/Chromium configurado.
    Detecta automáticamente si usar Google Chrome o Chromium.
    
    Returns:
        webdriver.Chrome: Instancia del driver configurado
    
    Raises:
        Exception: Si no se puede inicializar el driver
    """
    
    # Opciones de Chrome
    options = webdriver.ChromeOptions()
    
    # Configuración para evitar detección como bot
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Otras configuraciones útiles
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    
    # Detectar qué navegador está disponible
    chrome_binary = None
    chrome_type = ChromeType.GOOGLE
    
    # Buscar Chromium primero (más común en Linux)
    if shutil.which('chromium-browser') or shutil.which('chromium'):
        chrome_binary = shutil.which('chromium-browser') or shutil.which('chromium')
        chrome_type = ChromeType.CHROMIUM
        options.binary_location = chrome_binary
    # Si no, buscar Google Chrome
    elif shutil.which('google-chrome') or shutil.which('google-chrome-stable'):
        chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
        chrome_type = ChromeType.GOOGLE
    else:
        raise Exception(
            "No se encontró Chrome ni Chromium instalado.\n"
            "Instala Chromium con: sudo apt install chromium-browser"
        )
    
    # Descargar/obtener el ChromeDriver correspondiente
    try:
        service = Service(ChromeDriverManager(chrome_type=chrome_type).install())
    except Exception as e:
        # Fallback: intentar sin especificar tipo
        try:
            service = Service(ChromeDriverManager().install())
        except:
            raise Exception(
                f"Error al descargar ChromeDriver: {e}\n"
                "Intenta limpiar la caché: rm -rf ~/.wdm"
            )
    
    # Inicializar el driver
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


def get_headless_driver():
    """
    Retorna un driver en modo headless (sin interfaz gráfica).
    Útil para servidores sin display o para testing.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Detectar navegador
    chrome_type = ChromeType.CHROMIUM if shutil.which('chromium-browser') else ChromeType.GOOGLE
    
    if shutil.which('chromium-browser') or shutil.which('chromium'):
        chrome_binary = shutil.which('chromium-browser') or shutil.which('chromium')
        options.binary_location = chrome_binary
    
    service = Service(ChromeDriverManager(chrome_type=chrome_type).install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver
