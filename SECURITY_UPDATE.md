# Actualización de Seguridad - Variables de Entorno

## ⚠️ IMPORTANTE - Configuración Requerida

La aplicación ahora usa variables de entorno para mayor seguridad. Sigue estos pasos:

## 1️⃣ Configuración Inicial (Solo primera vez)

Si es la primera vez que usas esta versión:

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Genera una clave secreta única
python3 -c "import secrets; print(secrets.token_hex(32))"

# Edita .env y reemplaza SECRET_KEY con la clave generada
nano .env  # o vim .env, o tu editor preferido
```

## 2️⃣ Qué cambió

### Antes (INSEGURO):
- La clave secreta estaba en el código: `app.secret_key = "Secret_Key_LinkedinAutomator_Alex"`
- Visible en el repositorio público

### Ahora (SEGURO):
- La clave se carga desde `.env`: `app.secret_key = os.getenv("SECRET_KEY")`
- El archivo `.env` está en `.gitignore` y NO se comparte

## 3️⃣ Verificar que funciona

```bash
# Activa tu entorno virtual
source venv/bin/activate

# Ejecuta Flask
flask run
```

Si ves errores, verifica que:
- ✅ Existe el archivo `.env` en la raíz del proyecto
- ✅ Contiene una línea: `SECRET_KEY=tu_clave_generada`
- ✅ `python-dotenv` está instalado (ya está en requirements.txt)

## 4️⃣ Archivos nuevos

- `.env` - Tu configuración privada (NO compartir)
- `.env.example` - Plantilla para otros usuarios
- `.gitignore` - Actualizado para proteger archivos sensibles

## ⚡ Nota para desarrolladores

Si clonas este repo en otro equipo, recuerda crear tu propio `.env` basándote en `.env.example`.
