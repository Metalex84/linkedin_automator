'
Copyright (c) 2024 [Alejandro Gonzalez Venegas]

Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
https://creativecommons.org/licenses/by-nc/4.0/
'

# Clonar el repositorio de GitHub
git clone https://github.com/Metalex84/linkedin_automator.git

# Cambiar al directorio clonado
Set-Location linkedin_automator

# Crear un entorno virtual de Python
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar las dependencias del proyecto
pip install -r requirements.txt

# Desactivar el entorno virtual
deactivate