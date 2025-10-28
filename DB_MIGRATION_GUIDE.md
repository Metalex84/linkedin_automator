# Guía de Migración - Base de Datos

## ⚠️ Atención: Cambios en el manejo de la base de datos

La base de datos `linkedin.db` ya **NO** se incluye en el repositorio de Git por razones de seguridad y privacidad.

## Para usuarios existentes

Si ya tenías el proyecto instalado y usabas `linkedin.db`:

### Opción 1: Mantener tu base de datos actual (Recomendado)
```bash
# Tu archivo linkedin.db ya existe y seguirá funcionando
# No necesitas hacer nada, solo asegúrate de que existe
ls -l linkedin.db
```

### Opción 2: Empezar de cero
```bash
# Respalda tu base de datos actual
mv linkedin.db linkedin.db.backup

# Crea una nueva base de datos vacía
python3 init_db.py
```

## Para nuevas instalaciones

Si clonas el proyecto por primera vez:

```bash
# Después de clonar el repositorio
git clone https://github.com/tu-usuario/linkedin_automator.git
cd linkedin_automator

# Configura el entorno
cp .env.example .env
# (Edita .env con tu SECRET_KEY)

# Inicializa la base de datos
python3 init_db.py
```

## ¿Por qué este cambio?

1. **Privacidad**: La base de datos contiene información de usuarios (hashes de contraseñas, datos de uso)
2. **Seguridad**: Cada instalación debe tener su propia base de datos
3. **Buenas prácticas**: Las bases de datos no deben versionarse en Git
4. **Tamaño**: Reduce el tamaño del repositorio

## Estructura de la base de datos

El script `init_db.py` crea la tabla `usuarios` con:

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    last_connection TEXT,
    connections_left INTEGER DEFAULT 0,
    messages_left INTEGER DEFAULT 0,
    visits_left INTEGER DEFAULT 0
)
```

## Resolución de problemas

**Error: "no such table: usuarios"**
```bash
python3 init_db.py
```

**Error: "unable to open database file"**
```bash
# Verifica permisos del directorio
ls -la
chmod 755 .
```

**Quiero recuperar mis datos de la versión antigua**
```bash
# Si hiciste backup
mv linkedin.db.backup linkedin.db
```
