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


## PARA INSTALAR

### Windows
Abre **PowerShell**, escribe ```ìnstall.ps1``` y pulsa ```INTRO```

### Linux / MacOS
Abre la **Terminal**^, escribe ```install.sh``` y pulsa ```INTRO```

## PARA EJECUTAR
1. **Con la terminal de comandos, desplázate a la carpeta ```linkedin_automator```**

2. **Arranca el entorno virtual:**

*Windows:*
```
.\venv\Scripts\Activate.ps1
```

*MacOS / Linux:*

```
source venv/bin/activate
```

3. **Ejecuta el servicio:**
```
flask run
```

4. **Carga esta dirección en cualquier navegador:**
http://localhost:5000/

## PARA FINALIZAR
1. **Cuando hayas terminado, detén el servicio presionando** ```Ctrl + c```

2. **Desactiva el entorno virtual:**
```
deactivate
```