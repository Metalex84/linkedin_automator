from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from werkzeug.security import generate_password_hash, check_password_hash

# from cs50 import SQL
import controller as db

from datetime import datetime

from helpers import Persona, extract_username, wait_random_time, parse_time, number_of_pages, apology, login_required

import time
# import csv


app = Flask(__name__)



''' Configuro la session para utilizar el sistema de archivos en lugar de cookies '''
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



''' Configuro variables globales '''
app.config['opcion'] = None
app.config['driver'] = None
current_year = datetime.now().year



''' Configuro la base de datos '''
# db = SQL("sqlite:///linkedin.db")

    # TODO: control de registro forma de email: solo de la forma @juanpecarconsultores.com
    # TODO: funcion de escribir mensajes
    # TODO: funcion de enviar invitaciones, permitiendo personalizar mensaje de invitación ()
    # TODO: Control de errores: "texto_busqueda" vacio
    # TODO: implementar animación de espera mientras está funcionando
    # TODO: Función que actualice cuántos shots le quedan al usuario en el día
    # TODO: preguntar al usuario cuántas acciones quiere hacer hoy (maximo de 120 por seguridad)
    # TODO: contador regresivo para que, tras las acciones realizadas, el usuario vea cuántas le quedan durante el día.
    # TODO: último botón que permita al usuario descargar un archivo los datos recopilados
    # TODO: poner los datos de contacto en un CSV en una estructura legible para Pabbly -> HubSpot
    # TODO: permitir guardar las claves de LinkedIn aceptando un T & C de tratamiento de datos
    # TODO: ayuda del sistema
    # TODO: rellenar y guardar un historial de acciones realizadas



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
        # username = db.execute("SELECT usuario, connection, shots FROM usuarios WHERE id = ?", session["user_id"])
        user = db.get_user_by_id(session["user_id"])
        # return render_template('actions.html', current_year=current_year, username=username[0]["usuario"], connection=username[0]["connection"], shots=username[0]["shots"])
        return render_template('actions.html', current_year=current_year, username=user[0]["usuario"], connection=user[0]["connection"], shots=user[0]["shots"])
        
    else:
        return render_template('index.html', current_year=current_year)



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
        
        # cursor = db.execute("SELECT * FROM usuarios WHERE usuario = ?", request.form.get('username'))
        user = db.get_user_by_name(request.form.get('username'))

        if len(user) != 1 or not check_password_hash(user[0]['password'], request.form.get('password')):
            return apology('¡Usuario o contraseña incorrectos!', 403)
        
        session["user_id"] = user[0]['id']

        return render_template("actions.html", current_year=current_year, username=request.form.get('username'))

    else:
        return render_template('index.html', current_year=current_year)



@app.route("/logout")
def logout():
    '''
    Cierro la sesion del usuario guardando la fecha y hora de la ultima conexion
    '''
    # db.execute("UPDATE usuarios SET connection = ? WHERE id = ?", datetime.now(), session["user_id"])
    db.set_connection_by_id(datetime.now(), session["user_id"])
    session.clear()
    return redirect('/')



@app.route('/register', methods=['POST', 'GET'])
def register():
    '''
    1. Recupero los datos del formmulario de registro controlando posibles errores
    2. Aplico una función hash para almacenar la contraseña en la BD
    3. Asigno automáticamente 120 shots a cada usuario nuevo
    '''

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # cursor = db.execute("SELECT * FROM usuarios WHERE usuario = ?", username)
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
            # db.execute("INSERT INTO usuarios (usuario, password, shots) VALUES (?, ?, ?)", username, hash, 120)
            db.insert_user(username, hash, 120)
            return redirect("/")
    else:
        return render_template('register.html', current_year=current_year)



@app.route('/acciones', methods=['POST', 'GET'])
@login_required
def acciones():
    '''
    1. Recojo la opción seleccionada por el usuario, solo si tiene acciones disponibles restantes
    2. Devuelvo la acción seleccionada en forma de texto
    '''
    if request.method == 'POST':
        # acciones_restantes = db.execute("SELECT shots FROM usuarios WHERE id = ?", session["user_id"])
        acciones_restantes = db.get_shots_by_id(session["user_id"])
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
        
    else:
        if "user_id" in session:
            # username = db.execute("SELECT usuario FROM usuarios WHERE id = ?", session["user_id"])
            username = db.get_user_by_id(session["user_id"])
            return render_template('actions.html', current_year=current_year, username=username[0]["usuario"])
        else:
            return render_template('index.html', current_year=current_year)



@app.route('/help', methods=['GET'])
def help():
    return render_template('help.html', current_year=current_year)



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
        contrasena = request.form.get('password')
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
            return render_template('busqueda.html', usuario=usuario, current_year=current_year)
    else:
        return render_template('index.html', current_year=current_year)



@app.route('/viewprofile', methods=['GET'])
@login_required
def viewprofile():
    # username = db.execute("SELECT usuario, connection, shots FROM usuarios WHERE id = ?", session["user_id"])
    username = db.get_user_by_id(session["user_id"])
    return render_template('viewprofile.html', current_year=current_year, username=username[0]["usuario"], connection=username[0]["connection"], shots=username[0]["shots"])
        


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
        # ultima_conexion = db.execute("SELECT connection FROM usuarios WHERE id = ?", session["user_id"])
        ultima_conexion = db.get_connection_by_id(session["user_id"])
        formato = "%Y-%m-%d %H:%M:%S"
        last_connect = datetime.strptime(ultima_conexion[0]["connection"], formato)
        if last_connect.day() <= datetime.now().day():
            # db.execute("UPDATE usuarios SET shots = ? WHERE id = ?", 120, session["user_id"])
            db.set_shots_by_id(120, session["user_id"] )

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
            return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo='(sin resultados)')
        except NoSuchElementException:
            # Obtengo cantidad de resultados y calculo numero de paginas
            str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
            num_pags = number_of_pages(str_results)

            # Comienzo bucle externo
            pagina = 1
            # TODO: limitador para evitar que se hagan demasiadas peticiones
            while pagina <= num_pags:
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
                        usuario = extract_username(p_url)

                        # Esto solo me sirve a efectos de depuración
                        print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        
                        if opt == '1':
                            # VISITA: abro el perfil en una nueva pestaña:
                            # TODO: limitarlo porque el navegador puede cerrarse inesperadamente si se abren demasiadas pestañas
                            app.config['driver'].execute_script(f"window.open('{p_url}');")
                        elif opt == '2':
                            # ENVIO DE MENSAJES
                            # Cada boton de "Enviar mensaje" está en este path
                            button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button/span"
                            accion = app.config['driver'].find_element(By.XPATH, button)
                            accion.click()
                            # Recupero el texto del mensaje que deseo enviar
                            texto_mensaje = request.form.get('mensaje')
                            # Para la personalizacion, quedarme solo con el primer nombre.
                            texto_mensaje = texto_mensaje.replace('[[]]', nombre.split(' ')[0])
                            # TODO: escribir "texto_mensaje" en el recuadro del mensaje y enviarlo
                            
                        elif opt == '3':
                            # Cada botón "Conectar" está en este path
                            button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button/span"
                            accion = app.config['driver'].find_element(By.XPATH, button)
                            accion.click()
                            # Recupero el texto del mensaje que deseo enviar
                            texto_mensaje = request.form.get('mensaje')
                            # Para la personalizacion, quedarme solo con el primer nombre.
                            texto_mensaje = texto_mensaje.replace('[[]]', nombre.split(' ')[0])
                            # TODO: escribir "texto_mensaje" en el recuadro del mensaje y enviarlo
                            # TODO: pendiente de saltar contactos cuyo button no sea del tipo "Conectar"
                            # app.config['driver'].execute_script("arguments[0].click();", button)

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
            # shots_restantes = db.execute("SELECT shots FROM usuarios WHERE id = ?", session["user_id"])
            shots_restantes = db.get_shots_by_id(session["user_id"])
            db.set_shots_by_id(shots_restantes[0]['shots'] - shots_gastados, session["user_id"] )
            # db.execute("UPDATE usuarios SET shots = ? WHERE id = ?", shots_restantes - shots_gastados, session["user_id"])
            return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=shots_gastados)








        '''
        if opt == '1':
            
            # VISITAR PERFILES / RECOPILAR INFORMACIÓN BÁSICA
            # Esta opcion excluye los contactos de primer grado, por lo que me quedo solo con los contactos de profundidad 2 y 3
            
    
            deep = '&network=%5B"S"%2C"O"%5D'
            app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")
            
            start = time.time()
            end = 0.0
            
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el empty-state;
            try:
                app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
                # Si la excepción no salta, es que no se han producido resultados de búsqueda. Por lo tanto, voy a la última página notificando que no hay resultados
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo='(sin resultados)')

            except NoSuchElementException:
                # Con esto averiguo cuantos resultados de busqueda se han producido y calculo el numero total de paginas.
                # TODO: ¿podria ser necesario controlar esto con otro try-except?
                str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
                num_pags = number_of_pages(str_results)
                
                pagina = 1
                while pagina <= num_pags:
                    # Primero me posiciono en la página de búsqueda y espero un poco
                    app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                    wait_random_time()

                    # Construyo la lista de perfiles a visitar
                    profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                    visit_profiles = [p for p in profiles]

                    i = 1
                    for p in visit_profiles:
                        
                        # Si no encuentra el elemento del nombre, capturo excepcion y salto al siguiente
                        try:
                            # Este path es el del nombre completo, pero si pone "Miembro de LinkedIn", no existe, por lo que se lanza otra excepcion
                            path_name = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[1]/div/span[1]/span/a/span/span[1]"
                            path_role = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[2]"
                            nombre = app.config['driver'].find_element(By.XPATH, path_name).text
                            rol = app.config['driver'].find_element(By.XPATH, path_role).text
                            
                            # Esto de momento no hace nada, pero podría ser interesante conservar esta información: traer datos en JSON, adjuntar URL de perfil en CSV, etc.
                            p_url = p.get_attribute('href')
                            usuario = extract_username(p_url)
                            
                            # Si quiero abrir en una nueva pestaña:
                            # app.config['driver'].execute_script(f"window.open('{p_url}');")
                            
                            # Esto solo me sirve a efectos de depuración
                            print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                            
                            # Agrego el contacto a la lista
                            contacto = Persona(nombre, rol)
                            perfiles_visitados.append(contacto)

                        except NoSuchElementException:
                            pass
                        finally:
                            i += 1
                            wait_random_time()
                    pagina += 1
                end = time.time()
                app.config['driver'].quit()
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=len(perfiles_visitados))
         
        elif opt == '2':
             
            # ENVIAR MENSAJES A PERSONAS DE MI RED DE CONTACTOS 
            # Esto solo tiene efecto con los contactos de primer grado (profundidad 1)
            
            
            deep = '&network=%5B"F"%5D'
            app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")

            start = time.time()
            end = 0.0
            
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el empty-state;
            try:
                app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
                # Si la excepción no salta, es que no se han producido resultados de búsqueda. Por lo tanto, voy a la última página notificando que no hay resultados
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo='(sin resultados)')

            except NoSuchElementException:
                # Con esto averiguo cuantos resultados de busqueda se han producido y calculo el numero total de paginas.
                str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
                num_pags = number_of_pages(str_results)
                
                pagina = 1
                while pagina <= num_pags:
                    # Primero me posiciono en la página de búsqueda y espero un poco
                    app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                    wait_random_time()

                    # Construyo la lista de perfiles a visitar
                    profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                    visit_profiles = [p for p in profiles]

                    i = 1
                    for p in visit_profiles:
                        p_url = p.get_attribute('href')
                        usuario = extract_username(p_url)
    
                        # Recupero los datos del perfil sobre el que realizo la acción
                        path_name = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]"
                        path_role = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div[1]/div[2]"
 
                        nombre = app.config['driver'].find_element(By.XPATH, path_name).text
                        rol = app.config['driver'].find_element(By.XPATH, path_role).text
                        print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        contacto = Persona(nombre, rol)
                        perfiles_visitados.append(contacto)    

                        # XPath para cada boton de "Enviar mensaje" 
                        msg = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button/span"
                        # TODO: ¿Encerrar esto en un try?
                        enviar_mensaje = app.config['driver'].find_element(By.XPATH, msg)
                        enviar_mensaje.click()

                        # TODO: para la personalizacion, quedarme solo con el primer nombre. Revisa estas dos lineas:
                        # primernombre = nombre.split(' ')
                        # primernombre[0] = primernombre[0].capitalize()
                        

                        i += 1
                        wait_random_time()
                    pagina += 1
                end = time.time()
                app.config['driver'].quit()
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=len(perfiles_visitados))
                    
        elif opt == '3':
            
            # ENVIAR INVITACIONES DE CONTACTO


            # Incluyo los contactos de segundo y tercer grado (profundidad 2 y 3), porque algunos contactos de tercer grado admiten invitaciones
            deep = '&network=%5B"S"%2C"O"%5D'
            
            app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")

            start = time.time()
            end = 0.0
            
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el empty-state;
            try:
                app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
                # Si la excepción no salta, es que no se han producido resultados de búsqueda. Por lo tanto, voy a la última página notificando que no hay resultados
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo='(sin resultados)')

            except NoSuchElementException:
                # Con esto averiguo cuantos resultados de busqueda se han producido y calculo el numero total de paginas.
                str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
                num_pags = number_of_pages(str_results)
                
                pagina = 1
                # TODO: En pruebas. Solo lo hago de una pagina
                num_pags = 1
                while pagina <= num_pags:
                    # Primero me posiciono en la página de búsqueda y espero un poco
                    app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                    wait_random_time()
                
                    # Construyo la lista de perfiles a visitar
                    profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                    visit_profiles = [p for p in profiles]

                    i = 1
                    for p in visit_profiles:
                        p_url = p.get_attribute('href')
                        usuario = extract_username(p_url)

                        # Cada botón "Conectar" está en este path
                        button = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[3]/div/button/span"
                        conectar = app.config['driver'].find_element(By.XPATH, button)
                        conectar.click()
                        
                        # Esto es lo que envía la solicitud de contacto como tal
                        # TODO: pendiente de saltar contactos cuyo button no sea del tipo "Conectar"
                        app.config['driver'].execute_script("arguments[0].click();", button)
                        

                        # Recupero los datos del perfil sobre el que realizo la acción
                        path_name = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]"
                        path_role = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div[1]/div[2]"
                        nombre = app.config['driver'].find_element(By.XPATH, path_name).text
                        rol = app.config['driver'].find_element(By.XPATH, path_role).text
                        print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        contacto = Persona(nombre, rol)
                        perfiles_visitados.append(contacto)
                        i += 1
                        wait_random_time()
                    pagina += 1
                end = time.time()
                app.config['driver'].quit()
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=len(perfiles_visitados))
    
        else:
            app.config['driver'].quit()
            return('Aqui ha pasado algo raro...')
        '''
    else:
        app.config['driver'].quit()
        return render_template('index.html', current_year=current_year)



if __name__ == '__main__':
    app.run()


    '''
    Al final habrá que hacer un área privada con preferencias de cada cual, con mapeo de las visitas (quién está conectado), y que se guarden
    las preferencias de cada usuario (credenciales de Linkedin, preferencias de busqueda, rol en la empresa, fotos, etcétera).
    '''