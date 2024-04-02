from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from werkzeug.security import generate_password_hash, check_password_hash
from linkedin_api import Linkedin

from cs50 import SQL

from urllib.parse import urlparse
from datetime import datetime

from helpers import apology, login_required

import random
import time
import math
import csv


# Configuro la aplicacion
app = Flask(__name__)

# Configuro la sesion para utilizar el sistema de archivos en lugar de cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configuro variables globales
app.config['opcion'] = None
app.config['driver'] = None
app.config['api'] = None
app.config['counter'] = 0
current_year = datetime.now().year

# Configuro la base de datos
db = SQL("sqlite:///linkedin.db")

# Funcion que parsea la url para extraer el nombre de usuario de LinkedIn
def extract_username(url):
    parsed_url = urlparse(url)
    path_comp = parsed_url.path.split('/')
    if len(path_comp) > 2:
        return path_comp[2]
    else:
        return None
    

# Funcion que convierte el tiempo en segundos a un formato de horas, minutos y segundos
def parse_time(seconds):
    horas = int (seconds // 3600)
    minutos = int ((seconds % 3600) // 60)
    segundos = int (seconds % 60)
    resultado = f"{horas} horas, {minutos} minutos y {segundos} segundos"
    return resultado



@app.after_request
def after_request(response):
    """Me aseguro de que los response no se almacenan en cache"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

    # TODO: Función que actualice cuántos shots le quedan al usuario en el día
    # TODO: A profundidad 1 -> escribir mensajes a contactos. (NO COMBINAR PROFUNDIDADES)
    # TODO: A profundidad 2 -> enviar invitaciones a contactos y visita de perfiles
    # TODO: A profundidad 3 -> visitar perfiles
    # TODO: tratar de recopilar nombre y cargo de cada perfil antes de visitarlo. 
    #       Si no se puede, quedarme con nombre extraido de url y utilizar linkedin_api para obtener los datos.
    # TODO: preguntar al usuario cuántas acciones quiere hacer hoy (maximo de 120 por seguridad)
    # TODO: implementar un contador regresivo para que, tras las acciones realizadas, el usuario vea cuántas le quedan durante el día.
    # TODO: implementar un último botón que permita al usuario descargar un archivo con el reporte de las acciones realizadas (y datos de contacto si se han recopilado)
    # TODO: en esto ultimo, si o si los datos de contacto en un CSV en una estructura legible para Pabbly -> HubSpot


@app.route('/')
@login_required
def index():
    ''' De momento solo muestro el nombre de usuario en la página principal para verificar que el login se ha producido '''
    db.execute("SELECT usuario FROM usuarios WHERE id = ?", session["user_id"])
    return render_template('index.html', current_year=current_year)



@app.route('/login', methods=['POST', 'GET'])
def login():
    # Borro posibles sesiones abiertas
    session.clear()

    # Me aseguro de que vengo del formmulario de login
    if request.method == 'POST':
        
        # Y me aseguro de que no hay campos vacios
        if not request.form.get('username'):
            return apology('¡Introduce tu nombre de usuario!', 403)
        elif not request.form.get('password'):
            return apology('¡Introduce tu contraseña!', 403)
        
        # Pregunto a la base de datos si el usuario existe
        cursor = db.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", request.form.get('username')
        )

        # Y me aseguro de que la contraseña es correcta
        if len(cursor) != 1 or not check_password_hash(
            cursor[0]["password"], request.form.get('password')
        ):
            return apology('¡Usuario o contraseña incorrectos!', 403)
        
        # Almaceno el usuario que se ha logueado
        session["user_id"] = cursor[0]["id"]

        # Si todo fue bien, redirijo a la página de acciones
        return render_template("actions.html", current_year=current_year, username=request.form.get('username'))

    # Si vengo por GET, muestro el formulario de login directamente
    else:
        return render_template('index.html', current_year=current_year)



@app.route("/logout")
def logout():
    print("Ultima conexion: ", datetime.now())
    db.execute(
        "UPDATE usuarios SET connection = ? WHERE usuario = ?", datetime.now(), session["user_id"]
        )
    session.clear()
    return render_template('index.html', current_year=current_year)



@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        cursor = db.execute("SELECT * FROM usuarios WHERE usuario = ?", username)

        if not username:
            return apology("¡Introduce un nombre de usuario!", 400)
        elif len(cursor) != 0:
            return apology("¡Este nombre de usuario ya existe!", 400)
        elif not password:
            return apology("¡Introduce una contraseña!", 400)
        elif not confirmation:
            return apology("¡Confirma tu contraseña!", 400)
        elif password != confirmation:
            return apology("¡Las contraseñas no coinciden!", 400)
        else:
            # Funcion de hash para la contraseña
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            # Inserto el usuario en la base de datos
            db.execute("INSERT INTO usuarios (usuario, password, shots) VALUES (?, ?, ?)", username, hash, 120)
            return redirect("/")
    else:
        return render_template('register.html', current_year=current_year)



@app.route('/acciones', methods=['POST', 'GET'])
@login_required
def acciones():
    # Si vengo por POST, recojo la opción seleccionada por el usuario
    if request.method == 'POST':
        # Esto solo se ejecutará si el usuario tiene acciones disponibles en el día.
        acciones_restantes = db.execute("SELECT shots FROM usuarios WHERE id = ?", session["user_id"])
        if acciones_restantes[0]['shots'] == 0:
            return apology('¡No tienes acciones disponibles hoy!', 403)
        else:
            accion = ''
            app.config['opcion'] = request.form.get('opciones')
            opt = app.config['opcion']
            if opt == '1':
                accion = 'visitar perfiles'
            elif opt == '2':
                accion = 'escribir mensajes'
            elif opt == '3':
                accion = 'enviar invitaciones'
            return render_template('linklogin.html', current_year=current_year, accion=accion)
        
    # Si vengo por GET, redirijo a la página de login
    else:
        return render_template('index.html', current_year=current_year)



@app.route('/linklogin', methods=['POST', 'GET'])
@login_required
def linklogin():
    if request.method == 'POST':
        app.config['driver'] = webdriver.Chrome()
        app.config['driver'].maximize_window()
        usuario = request.form.get('username')
        contrasena = request.form.get('password')
        app.config['api'] = Linkedin(usuario, contrasena)
        app.config['driver'].get('https://www.linkedin.com')
        username = app.config['driver'].find_element(By.XPATH, '//*[@id="session_key"]')
        password = app.config['driver'].find_element(By.XPATH, '//*[@id="session_password"]')
        username.send_keys(usuario)
        password.send_keys(contrasena)
        submit = app.config['driver'].find_element(By.XPATH, '//button[@type="submit"]')
        submit.click()
        time.sleep(random.randint(1, 4))

        # Compruebo si el acceso a LinkedIn se ha hecho correctamente
        if app.config['driver'].current_url == 'https://www.linkedin.com/uas/login-submit':
            return apology('¡Usuario o contraseña de LinkedIn incorrectos!', 403)
        else:
            return render_template('busqueda.html', usuario=usuario, current_year=current_year)
    else:
        return render_template('index.html', current_year=current_year)



@app.route('/busqueda', methods=['POST', 'GET'])
@login_required
def busqueda():
    if request.method == 'POST':
        opt = app.config['opcion']
        perfiles_visitados = []
        cuadro_texto = request.form.get('texto_busqueda')

        # Recupero la profundidad de la red (contactos de segundo grado, de tercer grado o todos los contactos)
        grado = request.form.get('grado')
        if grado == 'grade1':
            deep = '&network=%5B"F"%5D'
        elif grado == 'grade2':
            deep = '&network=%5B"S"%5D'
        elif grado == 'grade3':
            deep = '&network=%5B"O"%5D'
        else:
            deep = ''
        
        if opt == '1':
            start = time.time()
            end = 0.0
            contact_info = []
            app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")

            # Si la busqueda no ha producido resultados, capturo la excepción y devuelvo un mensaje de error
            try:
                app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
            except NoSuchElementException:
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo='(sin resultados)')
        
            # Con esto averiguo cuantos resultados de busqueda se han producido.
            str_results = app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "pb2 t-black--light t-14")]')
            num_results = str_results.text.split(' ')
            try:
                # Si el número de resultados es mayor a 999, el texto se divide en dos partes
                resultados = int(num_results[0])
            except ValueError:
                buffer = num_results[1].split('.')
                resultados = int(buffer[0].join(buffer[1]))
            finally:
                num_pags = math.ceil(resultados / 10)

            pagina = 1
            # TODO: Esto lo tendremos que modificar para limitar el número de perfiles visitados por día.
            num_pags = 2
            while pagina <= num_pags:
                # Primero me posiciono en la página de búsqueda y espero un poco
                app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                time.sleep(random.randint(1, 4))

                # Construyo la lista de perfiles a visitar
                profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                visit_profiles = [p for p in profiles]
                i = 1
                for p in visit_profiles:
                    p_url = p.get_attribute('href')
                    # app.config['driver'].execute_script(f"window.open('{p_url}');")
                    usuario = extract_username(p_url)
                    # contact_info.append(app.config['api'].get_profile_contact_info(usuario)
                    path = f'*//li[{i}]/div/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]'
                    nombre = app.config['driver'].find_element(By.XPATH, path).text
                    print(f'El perfil de {nombre} se identifica como {usuario}')
                    perfiles_visitados.append(nombre)
                    i += 1
                    time.sleep(random.randint(1, 4))
                
                # Ahora construyo la lista de nombres propios
                '''
                nombres_usuarios = app.config['driver'].find_elements(By.XPATH, '//span[@aria-hidden="true"]')
                names = [n.text for n in nombres_usuarios if len(n.text) > 0]
                for n in names:
                    perfiles_visitados.append(n)
                '''
                pagina += 1
            '''    
            archivo = 'datos_contacto.csv'
            with open(archivo, mode='w', newline='') as f:
                writer = csv.writer(f)
                for row in contact_info:
                    writer.writerow(row)
            '''
            end = time.time()
            return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=parse_time(round(end - start, 2)))

        elif opt == '2':
            app.config['driver'].quit()
            return('Escribir mensajes no implementado aun')
            # TODO
            
        elif opt == '3':
            app.config['driver'].quit()
            return('Enviar invitaciones no implementado aun')
            # Para conectar seria: app.config['driver'].execute_script("arguments[0].click();", p)
            # TODO

        else:
            app.config['driver'].quit()
            return('Aqui ha pasado algo raro...')
    else:
        return render_template('index.html', current_year=current_year)



if __name__ == '__main__':
    app.run()


    '''
    Al final habrá que hacer un área privada con preferencias de cada cual, con mapeo de las visitas (quién está conectado), y que se guarden
    las preferencias de cada usuario (credenciales de Linkedin, preferencias de busqueda, rol en la empresa, fotos, etcétera).
    '''