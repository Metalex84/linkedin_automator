from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from werkzeug.security import generate_password_hash, check_password_hash

import model as db

from datetime import datetime

from helpers import Persona, wait_random_time, parse_time, number_of_pages, apology, login_required

import time
# import csv


app = Flask(__name__)



''' Configuro la session para utilizar el sistema de archivos en lugar de cookies '''
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



''' Configuro variables globales y constantes'''
app.config['opcion'] = None
app.config['driver'] = None
app.config['texto_mensaje'] = None
MAX_SHOTS = 120
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"



    # TODO: implementar ayuda
    # TODO: control de registro forma de email: solo de la forma @juanpecarconsultores.com u horecarentable.com o ayira.es
    # TODO: funcion de escribir mensajes
    # TODO: funcion de enviar invitaciones, permitiendo personalizar mensaje de invitación (OJO, ELEMENTS NOT CLICKABLE)
    # TODO: implementar animación de espera mientras está funcionando
    # TODO: preguntar al usuario cuántas acciones quiere hacer en cada ciclo de trabajo
    # TODO: último botón que permita al usuario descargar un archivo los datos recopilados
    # TODO: poner los datos de contacto en un CSV en una estructura legible para Pabbly -> HubSpot
    # TODO: permitir guardar las claves de LinkedIn aceptando un T & C de tratamiento de datos
    # TODO: rellenar y guardar un historial de acciones realizadas
    # TODO: extraer todos los XPath a un fichero de configuración (strings.py o algo asi)
    # TODO: cambiar el renderizador de mensajes de error por uno propio
    # TODO: ajustar anchura de los cuadros de texto de pedir datos
    # TODO: controlar mostrar / ocultar la contraseña de LinkedIn mientras se está escribiendo
    # TODO: categorizar y discriminar los mensajes de error



@app.after_request
def after_request(response):
    ''' Me aseguro de que las páginas no se almacenen en la cache del navegador'''
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route('/')
@login_required
def index():
    if "user_id" in session:
        user = db.get_user_by_id(session["user_id"])
        return render_template('actions.html', current_year=datetime.now().year, username=user["usuario"], connection=user["connection"], shots=user["shots"])
        
    else:
        return render_template('index.html', current_year=datetime.now().year)



@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    1. Borro posibles sesiones abiertas
    2. Me aseguro de que no hay campos vacios
    3. Pregunto a la BD si el usuario existe y me aseguro de que la contraseña es correcta
    4. Almaceno el usuario que se ha logueado
    5. Si todo fue bien, redirijo a la página de acciones
    '''

    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return apology('¡Introduce tu nombre de usuario!', 403)
        elif not request.form.get('password'):
            return apology('¡Introduce tu contraseña!', 403)
        
        user = db.get_user_by_name(request.form.get('username'))

        if len(user) != 1 or not check_password_hash(user[0]['password'], request.form.get('password')):
            return apology('¡Usuario o contraseña incorrectos!', 403)
        
        session["user_id"] = user[0]['id']

        return render_template("actions.html", current_year=datetime.now().year, username=request.form.get('username'))

    else:
        return render_template('index.html', current_year=datetime.now().year)



@app.route("/logout")
def logout():
    '''
    Cierro la sesion del usuario guardando la fecha y hora de la ultima conexion
    '''
    db.set_connection_by_id(datetime.now().strftime(DATE_FORMAT), session["user_id"])
    session.clear()
    return redirect('/')



@app.route('/register', methods=['POST', 'GET'])
def register():
    '''
    1. Recupero los datos del formmulario de registro controlando posibles errores
    2. Aplico una función hash para almacenar la contraseña en la BD
    3. Asigno el máximo de shots a cada usuario nuevo
    '''

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        cursor = db.get_user_by_name(username)

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
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.insert_user(username, hash, MAX_SHOTS)
            return redirect("/")
    else:
        return render_template('register.html', current_year=datetime.now().year)



@app.route('/acciones', methods=['POST', 'GET'])
@login_required
def acciones():
    '''
    1. Recojo la opción seleccionada por el usuario, solo si tiene acciones disponibles restantes
    2. Devuelvo la acción seleccionada en forma de texto
    '''
    if request.method == 'POST':
        # TODO: verificar que pasa si el usuario se queda sin shots
        acciones_restantes = db.get_shots_by_id(session["user_id"])
        if acciones_restantes == 0:
            return apology('¡No tienes acciones disponibles hoy!', 403)
        else:
            accion = ''
            app.config['opcion'] = request.form.get('opciones')
            opt = app.config['opcion']
            if opt == '1':
                accion = 'visitar perfiles'
            elif opt == '2':
                accion = 'escribir mensajes'
                # Recupero el texto del mensaje que deseo enviar
                app.config['texto_mensaje'] = request.form.get('mensaje')
                if not app.config['texto_mensaje']:
                    return apology('¡Introduce un mensaje!', 403)
            elif opt == '3':
                accion = 'enviar invitaciones'
                # Recupero el texto del mensaje que deseo enviar
                app.config['texto_mensaje'] = request.form.get('mensaje')
                if not app.config['texto_mensaje']:
                    return apology('¡Introduce un mensaje!', 403)
            return render_template('linklogin.html', current_year=datetime.now().year, accion=accion)
        
    else:
        if "user_id" in session:
            username = db.get_user_by_id(session["user_id"])
            return render_template('actions.html', current_year=datetime.now().year, username=username["usuario"])
        else:
            return render_template('index.html', current_year=datetime.now().year)



@app.route('/help', methods=['GET'])
def help():
    return render_template('help.html', current_year=datetime.now().year)



@app.route('/linklogin', methods=['POST', 'GET'])
@login_required
def linklogin():
    '''
    1. Abro navegador, uso las claves de acceso de LinkedIn y redirijo a la página de busqueda
    2. Controlo posible fallo de login, devolviendo un mensaje de error
    '''
    if request.method == 'POST':
        app.config['driver'] = webdriver.Chrome()
        app.config['driver'].maximize_window()
        usuario = request.form.get('username')
        if not usuario:
            return apology('¡Introduce tu usuario de LinkedIn!', 403)
        contrasena = request.form.get('password')
        if not contrasena:
            return apology('¡Introduce tu contraseña de LinkedIn!', 403)
        app.config['driver'].get('https://www.linkedin.com')
        username = app.config['driver'].find_element(By.XPATH, '//*[@id="session_key"]')
        password = app.config['driver'].find_element(By.XPATH, '//*[@id="session_password"]')
        username.send_keys(usuario)
        password.send_keys(contrasena)
        submit = app.config['driver'].find_element(By.XPATH, '//button[@type="submit"]')
        submit.click()
        wait_random_time()

        if app.config['driver'].current_url == 'https://www.linkedin.com/uas/login-submit':
            return apology('¡Usuario o contraseña de LinkedIn incorrectos!', 403)
        else:
            remaining_shots = db.get_shots_by_id(session["user_id"])
            return render_template('busqueda.html', usuario=usuario, current_year=datetime.now().year, remaining_shots=remaining_shots)
    else:
        return render_template('index.html', current_year=datetime.now().year)



@app.route('/viewprofile', methods=['GET'])
@login_required
def viewprofile():
    username = db.get_user_by_id(session["user_id"])
    return render_template('viewprofile.html', current_year=datetime.now().year, username=username["usuario"], connection=username["connection"], shots=username["shots"])
        


@app.route('/busqueda', methods=['POST', 'GET'])
@login_required
def busqueda():
    '''
    1. Recupero la opción y en base a ella ejecuto unas u otras funciones
    2. Recupero el texto de busqueda y realizo la busqueda 
    '''
    if request.method == 'POST':
        perfiles_visitados = []
        cuadro_texto = request.form.get('texto_busqueda')
        opt = app.config['opcion']

        # TODO: verificar si funciona el reseteo del contador de shots 
        ultima_conexion = db.get_connection_by_id(session["user_id"])
        if ultima_conexion is not None:
            last_connect = datetime.strptime(ultima_conexion, DATE_FORMAT)            
            if last_connect.date() < datetime.now().date():
                db.set_shots_by_id(MAX_SHOTS, session["user_id"] )

        # Discrimino profundidad en base a opcion
        if opt == '1' or opt == '3':
            deep = '&network=%5B"S"%2C"O"%5D'
        elif opt == '2':
            deep = '&network=%5B"F"%5D'

        # Cargo pagina de busqueda para averiguar cuantas vueltas daran los bucles
        app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")

        # Empiezo a contar el tiempo
        start = time.time()
        end = 0.0

        try:
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el 'empty-state';
            app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
            return render_template("done.html", profiles=perfiles_visitados, current_year=datetime.now().year, tiempo='(sin resultados)')
        except NoSuchElementException:
            # Obtengo cantidad de resultados y calculo numero de paginas
            str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
            num_pags = number_of_pages(str_results)

            # Comienzo bucle externo. Si he llegado aquí, siempre debería encontrar al menos 1 página.
            pagina = 1
            # Obtengo los shots restantes del usuario, porque no rebasarlos es una condición complementaria de parada
            remaining_shots = db.get_shots_by_id(session["user_id"])
            while pagina <= num_pags and len(perfiles_visitados) <= remaining_shots:  
                # Recargo la pagina de busqueda y espero un poco
                app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                wait_random_time()
                # Construyo la lista de perfiles a visitar en esa pagina (LinkedIn muestra maximo 10 por cada una)
                profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                visit_profiles = [p for p in profiles]
                # Itero sobre la lista de perfiles de cada pagina
                i = 1
                for p in visit_profiles:
                    try:
                        # Si 'p' fuese un "Miembro de LinkedIn", estos elementos no existirias, por lo que se lanzaria otra excepcion, que capturo y salto al siguiente perfil
                        path_name = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[1]/div/span[1]/span/a/span/span[1]"
                        path_role = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[2]"
                        nombre = app.config['driver'].find_element(By.XPATH, path_name).text
                        rol = app.config['driver'].find_element(By.XPATH, path_role).text
                        
                        # Guardo tambien el enlace al perfil
                        p_url = p.get_attribute('href')
                        
                        # Puede que más adelante necesite hacer algo con el nombre de usuario de LinkedIn de cada contacto
                        # usuario = extract_username(p_url)

                        # Y esto solo me sirve a efectos de depuración
                        # print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        
                        if opt == '1':
                            # VISITA: abro el perfil en una nueva pestaña:
                            # TODO: limitarlo porque el navegador puede cerrarse inesperadamente si se abren demasiadas pestañas
                            app.config['driver'].execute_script(f"window.open('{p_url}');")
                        elif opt == '2':
                            # ENVIO DE MENSAJES
                            if len(visit_profiles) == 1:
                                # Path del boton "Enviar mensaje" si solo hay un perfil en la pagina
                                button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li/div/div/div/div[3]/div/div/button"
                            else:
                                # Path del boton "Enviar mensaje" si hay mas de un perfil en la pagina
                                button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button"
                            app.config['driver'].find_element(By.XPATH, button).click()
                            
                            # Para la personalizacion, quedarme solo con el nombre.
                            mensaje = app.config['texto_mensaje'].replace('[[]]', nombre.split(' ')[0])
                            
                            # TODO: Depurar poner el "mensaje" en el recuadro y lanzarlo
                            app.config['driver'].find_element(By.XPATH, f"//div[4]/aside[1]/div[{i+1}]/div[1]/div[2]/div/form/div[2]").click()
                            
                            fieldtext = app.config['driver'].find_elements(By.TAG_NAME, "p")
                            fieldtext[i].send_keys(mensaje)
                            fieldtext[i].send_keys(Keys.RETURN)
                            

                            
                        elif opt == '3':
                            # Cada botón "Conectar" está en este path
                            button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button"
                            app.config['driver'].find_element(By.XPATH, button).click()
                            # Para la personalizacion, quedarme solo con el nombre.
                            mensaje = app.config['texto_mensaje'].replace('[[]]', nombre.split(' ')[0])
                            # Este es el boton de personalizar invitacion: /html/body/div[3]/div/div/div[3]/button[1]/span
                            # Este es el area de texto. Pongo "mensaje" en el recuadro y lo lanzo
                            textfield = app.config['driver'].find_element(By.XPATH, "/html/body/div[3]/div/div/div[3]/div[1]/textarea").send_keys(mensaje)
                            
                            app.config['driver'].find_element(By.XPATH, "/html/body/div[3]/div/div/div[4]/button[1]").click()
                            
                            # TODO: pendiente de saltar contactos cuyo button obligue a meter su email"
                            close = app.config['driver'].find_element(By.XPATH, '//button[@aria-label="Dismiss"]')
                            app.config['driver'].execute_script("arguments[0].click();", close)


                        else:
                            return apology('Esta accion no estaba prevista, ¡contacta con el desarrollador!', 405)
                        
                        # Agrego el contacto a la lista
                        contacto = Persona(nombre, rol, p_url)
                        perfiles_visitados.append(contacto)

                    except NoSuchElementException:
                        pass
                    finally:
                        i += 1
                        wait_random_time()
                pagina += 1

            # Paro el reloj, cierro el navegador, actualizo shots restantes y muestro resultados
            end = time.time()
            app.config['driver'].quit()
            shots_gastados = len(perfiles_visitados)
            shots_restantes = db.get_shots_by_id(session["user_id"])
            db.set_shots_by_id(shots_restantes - shots_gastados, session["user_id"] )
            return render_template("done.html", profiles=perfiles_visitados, current_year=datetime.now().year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=shots_gastados)

    else:
        app.config['driver'].quit()
        return render_template('index.html', current_year=datetime.now().year)



if __name__ == '__main__':
    app.run()

