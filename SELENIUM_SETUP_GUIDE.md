# Guía de Instalación de Selenium y ChromeDriver

## ⚠️ IMPORTANTE: Requisitos para Selenium

La aplicación necesita **Google Chrome o Chromium** para funcionar. El ChromeDriver se descarga automáticamente gracias a `webdriver-manager`.

## 📦 Instalación

### Opción 1: Chromium (Recomendado para Linux)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y chromium-browser

# Verificar instalación
chromium-browser --version
```

### Opción 2: Google Chrome

```bash
# Descargar e instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Verificar instalación
google-chrome --version
```

## 🧪 Verificar la instalación

Ejecuta el script de prueba:

```bash
source venv/bin/activate
python3 test_selenium.py
```

## 🔧 Solución de problemas comunes

### Error: "chrome not reachable"
**Causa**: Chrome/Chromium no está instalado.
**Solución**: Instala Chromium (ver arriba).

### Error: "ChromeDriver version mismatch"
**Causa**: Incompatibilidad de versiones.
**Solución**: `webdriver-manager` se encarga automáticamente. Si persiste:
```bash
rm -rf ~/.wdm
```

### Error: "No such file or directory: chromedriver"
**Causa**: ChromeDriver no se descargó correctamente.
**Solución**: Ejecuta manualmente:
```bash
python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Modo headless (sin interfaz gráfica)
Para servidores sin display, la aplicación usa automáticamente `--headless`.

## 📝 Notas

- **webdriver-manager** descarga automáticamente el ChromeDriver compatible
- El driver se guarda en `~/.wdm/` (no necesitas instalarlo manualmente)
- La primera ejecución puede tardar más (descarga el driver)

## 🚀 Ejecución después de instalar

```bash
source venv/bin/activate
flask run
```

Abre http://localhost:5000 en tu navegador.
