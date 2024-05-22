# LinkedIn Automator
<img src="static/LinkedIn_Logo.png" alt="LinkedIn Logo" width="100">

## Descripción
LinkedIn Automator es un **web-scrapper** que permite realizar búsquedas de personas en LinkedIn. 

Para ello, utiliza el webdriver de Google Chrome y un entorno virtual que tendrás que configurar (y te diré cómo).

**IMPORTANTE**: esta aplicación respeta las Condiciones de Uso de LinkedIn porque no plagia las características de ***Sales Navigator*** ni de ***LinkedIn Premium***

## Requisitos

* Es fundamental que [Google Chrome](https://www.google.com/intl/es_es/chrome/), [Python](https://www.python.org/downloads/) y [Git](https://git-scm.com/downloads?ref=allthings.how) estén instalados en tu equipo.
* Antes de empezar a utilizar la aplicación, es recomendable que inicies sesión manualmente en tu cuenta de LinkedIn con Google Chrome. 
    * *Es posible que LinkedIn Automator te muestre mensajes de error al intentar acceder a tu cuenta en tu nombre: se debe al control que hace LinkedIn de los posibles comportamientos de bot.*
    * *También es posible que durante la ejecución, LinkedIn te pida algún **código de verificación** o **'captcha'**; sigue las instrucciones en la pantalla.*

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
1. Descarga el fichero [install.ps1](https://github.com/Metalex84/linkedin_automator/blob/main/install.ps1)
2. Click derecho -> *"Ejecutar como script de PowerShell"*
3. Pulsa ```INTRO``` y ```Z``` para confirmar la ejecución

### Linux / MacOS
1. Descarga el fichero [install.sh](https://github.com/Metalex84/linkedin_automator/blob/main/install.sh)
2. Abre la terminal de comandos (**Terminal**)
3. Sitúate en la carpeta donde lo hayas descargado
4. Otorga permisos de ejecución al script: ```chmod +x install.sh```
4. Escribe ```./install.sh```
5. Pulsa ```INTRO``` 

## PARA EJECUTAR
### Windows
1. Descarga el fichero [run.ps1](https://github.com/Metalex84/linkedin_automator/blob/main/run.ps1)
2. Click derecho -> *"Ejecutar como script de PowerShell"*
3. Carga esta dirección en cualquier navegador:
```
http://localhost:5000/
```

### Linux / MacOS
1. Con la terminal de comandos, desplázate a la carpeta ```linkedin_automator```
2. Arranca el entorno virtual:
```
source venv/bin/activate
```
3. Ejecuta el servicio:
```
flask run
```
4. Carga esta dirección en cualquier navegador:
http://localhost:5000/

## PARA FINALIZAR
### Windows
1. Descarga el fichero [stop.ps1](https://github.com/Metalex84/linkedin_automator/blob/main/stop.ps1)
2. Click derecho -> *"Ejecutar como script de PowerShell"*

### Linux / MacOS
1. Detén el servicio presionando ```Ctrl + c```
2. Desactiva el entorno virtual:
```
deactivate
```