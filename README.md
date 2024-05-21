# LinkedIn Automator
<img src="static/LinkedIn_Logo.png" alt="LinkedIn Logo" width="100">

## Descripción
LinkedIn Automator es un **web-scrapper** que permite realizar búsquedas de personas en LinkedIn. 

Para ello, utiliza el webdriver de Google Chrome y un entorno virtual que tendrás que configurar (y te diré cómo).

**IMPORTANTE**: esta aplicación respeta las Condiciones de Uso de LinkedIn porque no plagia las características de ***Sales Navigator*** ni de ***LinkedIn Premium***

## Requisitos
* Es fundamental que [Google Chrome](https://www.google.com/chrome/), [Python](https://www.python.org/downloads/) y [Git](https://git-scm.com/downloads?ref=allthings.how) estén instalados en tu equipo.

### *Solo si utilizas Debian o Ubuntu*
***Tendrás que instalar Python de la siguiente manera***

```
sudo apt install python3 python3-venv
sudo apt install virtualenv python3-virtualenv
```


### *Solo si utilizas Windows*
***Necesitarás que tu terminal tenga permisos para ejecutar scripts:***

* *Abre **PowerShell** como administrador y ejecuta:* ```$ Get-ExecutionPolicy```
* *Si el retorno es* ```Unrestricted```*, significa que ya está habilitado*
* *Si el retorno es* ```Restricted```*, ejecuta:* ``` $ Set-ExecutionPolicy Unrestricted ```
* *Contesta con* ```S``` *o* ```Y``` *para confirmar el cambio*


## INSTALACIÓN Y EJECUCIÓN
Utiliza la terminal de comandos para instalar y ejecutar la aplicación en tu equipo:
1. **Clona este repositorio:**
```
git clone https://github.com/Metalex84/linkedin_automator.git
```

2. **Desplázate a la carpeta del proyecto**
```
cd linkedin_automator
```

3. **Instala el entorno virtual:**

*Windows:*
```
python -m venv venv
```

*MacOS / Linux:*
```
python3 -m venv venv
```

*Linux:*
```
python3 -m venv venv
```

4. **Arranca el entorno virtual:**

*Windows:*
```
.\venv\Scripts\Activate.ps1
```

*MacOS / Linux:*

```
source venv/bin/activate
```


5. **Instala las dependencias:**
```
pip install -r requirements.txt
```

6. **Ejecuta el servicio:**
```
flask run
```

7. **Carga esta dirección en cualquier navegador:**
http://localhost:5000/

8. **Cuando hayas terminado, detén el servicio presionando** ```Ctrl + c```

9. **Desactiva el entorno virtual:**
```
deactivate
```