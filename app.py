from flask import Flask, flash, redirect, render_template, url_for, request, session, jsonify, send_file
from flask_session import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options

from werkzeug.security import generate_password_hash, check_password_hash

from math import ceil
from datetime import datetime
from threading import Thread
import time
import csv

import helpers as h
import literals as l
import model as db


''' Configuro la aplicacion Flask y la clave secreta '''
app = Flask(__name__)
app.secret_key = "Secret_Key_LinkedinAutomator_Alex"



''' Configuro la session para utilizar el sistema de archivos en lugar de cookies '''
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


''' Configuro variables globales'''
app.config['driver'] = None
app.config['current_year'] = datetime.now().year
app.config['texto_mensaje'] = None
app.config['scrapping'] = None
app.config['tiempo'] = None
app.config['perfiles_visitados'] = []


@app.after_request
def after_request(response):
    ''' Me aseguro de que las páginas no se almacenen en la cache del navegador'''
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route('/')
@h.login_required
def index():
    if "user_id" in session:
        user = db.get_user_by_id(session["user_id"])
        return render_template('actions.html', username=user["usuario"])
        
    else:
        return render_template('index.html')
    


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

        # Recupero los datos del usuario. Si hay más de uno o si no coincide la contraseña, devuelvo un mensaje de error
        user = db.get_user_by_name(request.form.get('username'))
        if len(user) != 1 or not check_password_hash(user[0]['password'], request.form.get('password')):
            flash(l.ERR_USER_OR_PASS_WRONG)
            return render_template('index.html')

        # Guardo en sesión los datos que necesitaré del usuario mientras esté logueado
        session["user_id"] = user[0]['id']
        session["username"] = user[0]['usuario']
        session["connection"] = user[0]['connection']
        session["messages_left"] = user[0]['messages_left']
        session["connections_left"] = user[0]['connections_left']
        session["visits_left"] = user[0]['visits_left']
        

        # Consulto la ultima fecha de conexion del usuario
        ultima_conexion = db.get_last_connection_by_id(session["user_id"])
        # Hago esta comprobación para evitar errores en la primera conexión
        if ultima_conexion is not None:
            last_connect = datetime.strptime(ultima_conexion, l.DATE_FORMAT)            
            # Si ha pasado más de un día, reseteo los mensajes disponibles
            if last_connect.date() < datetime.now().date():
                db.set_messages_left_by_id(l.MAX_DAILY_MESSAGES, session["user_id"])
            # Si ha pasado más de un mes, reseteo las visitas disponibles
            if last_connect.month < datetime.now().month:
                db.set_visits_left_by_id(l.MAX_MONTHLY_VISITS, session["user_id"])
            # Si ha pasado más de una semana, reseteo las conexiones disponibles
            if last_connect.isocalendar()[1] < datetime.now().isocalendar()[1]:
                db.set_connections_left_by_id(l.MAX_WEEKLY_CONNECTIONS, session["user_id"])

        return render_template("actions.html")

    else:
        return render_template('index.html')



@app.route("/logout")
def logout():
    '''
    Cierro la sesion del usuario guardando la fecha y hora de la ultima conexion
    '''
    db.set_last_connection_by_id(datetime.now().strftime(l.DATE_FORMAT), session["user_id"])
    session.clear()
    return redirect(url_for('index'))



@app.route('/register', methods=['POST', 'GET'])
def register():
    '''
    1. Recupero los datos del formmulario de registro controlando posibles errores
    2. Aplico una función hash para almacenar la contraseña en la BD
    3. Como es usuario nuevo, le asigno el máximo de shots
    4. Guardo el usuario en sesión para, tras el registro, dirigirle a la página de acciones
    '''

    if request.method == "POST":
        # Recupero los datos del formulario
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Compruebo si el usuario ya existe en la BD
        cursor = db.get_user_by_name(username)
        if len(cursor) != 0:
            flash(l.ERR_USER_ALREADY_EXISTS)
            return redirect(url_for('register'))
        # O si no coinciden contraseña y confirmación
        elif password != confirmation:
            flash(l.ERR_PASSWORDS_NOT_MATCH)
            return redirect(url_for('register'))
        # O si el email no es válido
        elif not h.check_valid_username(username):
            flash(l.ERR_CORPORATE_EMAIL)
            return redirect(url_for('register'))
        else:
            # Genero contraseña cifrada e inserto todos los datos que conozco del usuario en la BD
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.insert_user(username, hash, l.MAX_WEEKLY_CONNECTIONS, l.MAX_DAILY_MESSAGES, l.MAX_MONTHLY_VISITS)
            
            # Recojo los datos del usuario recién registrado, asigno fecha y hora de conexión (actual) y guardo sus datos en sesión
            userdata = db.get_user_by_name(username)
            session["user_id"] = userdata[0]['id']
            db.set_last_connection_by_id(datetime.now().strftime(l.DATE_FORMAT), session["user_id"])
            session["username"] = userdata[0]['usuario']
            session["connection"] = userdata[0]['connection']
            session["messages_left"] = userdata[0]['messages_left']
            session["connections_left"] = userdata[0]['connections_left']
            session["visits_left"] = userdata[0]['visits_left']

            return redirect(url_for('acciones'))
    else:
        return render_template('register.html')



@app.route('/forgot', methods=['GET'])
def forgot():
    return render_template('reset.html')



@app.route('/reset', methods=['POST', 'GET'])
def reset():
    ''' Recojo la nueva contraseña y la confirmación, las comparo y actualizo la BD '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if password != confirmation:
            flash(l.ERR_PASSWORDS_NOT_MATCH)
            return redirect(url_for('reset'))
        else:
            user = db.get_user_by_name(username)
            if len(user) != 1:
                flash(l.ERR_USER_ALREADY_EXISTS)
                return redirect(url_for('reset'))
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.set_password_by_id(hash, user[0]['id'])
            return redirect(url_for('index'))
    else:
        return render_template('reset.html')



@app.route('/acciones', methods=['POST', 'GET'])
@h.login_required
def acciones():
    '''
    1. Recojo la opción seleccionada por el usuario, solo si tiene acciones disponibles restantes
    2. Devuelvo la acción seleccionada en forma de texto
    '''
    if request.method == 'POST':
        session['accion'] = ''
        session['opcion'] = request.form.get('opciones')
        if session.get('opcion') == '1':
            session['accion'] = l.ACTION_VISIT_PROFILES
        elif session.get('opcion') == '2':
            session['accion'] = l.ACTION_WRITE_MESSAGES
            # Recupero el texto del mensaje que deseo enviar
            app.config['texto_mensaje'] = request.form.get('mensaje')
            # Si el campo de texto está vacío, no puedo enviar ningún mensaje
            if not app.config['texto_mensaje']:
                flash(l.ERR_EMPTY_MESSAGE)
                return redirect(url_for('acciones'))
            # Si la cadena no contiene la secuencia de escape, el mensaje no se puede personalizar
            elif '----' not in app.config['texto_mensaje']:
                flash(l.ERR_WRONG_MESSAGE)
                return redirect(url_for('acciones'))
            
        elif session.get('opcion') == '3':
            session['accion'] = l.ACTION_SEND_CONNECTIONS
        return render_template('linklogin.html')
        
    else:
        if "user_id" in session:
            username = db.get_user_by_id(session["user_id"])
            return render_template('actions.html', username=username["usuario"])
        else:
            return render_template('index.html')



@app.route('/help', methods=['GET'])
def help():
    return render_template('help.html')



@app.route('/linklogin', methods=['POST', 'GET'])
@h.login_required
def linklogin():
    '''
    1. Abro navegador, uso las claves de acceso de LinkedIn y redirijo a la página de busqueda
    2. Controlo posible fallo de login, devolviendo un mensaje de error
    '''
    if request.method == 'POST':
        # Si no tengo los datos cogidos desde la sesión, los recojo del formulario
        if not (session.get('link_user') and session.get('link_pass')):
            usuario = request.form.get('username')
            contrasena = request.form.get('password')
            
            # En el HTML no son campos "required" porque si están en sesión no los necesito.
            # Pero si no están en sesión, valido si el usuario los introduce o no.
            if not usuario:
                flash(l.ERR_NO_LINKEDIN_USER)
                return redirect(url_for('linklogin'))
            elif not contrasena:
                flash(l.ERR_NO_LINKEDIN_PASS)
                return redirect(url_for('linklogin'))
        # Si ya tengo el login de linkedin en sesión, ya no lo vuelvo a pedir mientras dure la sesión
        else:
            usuario = session.get('link_user')
            contrasena = session.get('link_pass')
        
        # Abro navegador y redirijo a la página de LinkedIn
        
        '''
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        app.config['driver'] = webdriver.Chrome(options=chrome_options)
        '''
        
        app.config['driver'] = webdriver.Chrome()
        app.config['driver'].get(l.URL_LINKEDIN_HOME)
        try:
            username = app.config['driver'].find_element(By.XPATH, l.ELEMENT_SESSION_KEY)
            password = app.config['driver'].find_element(By.XPATH, l.ELEMENT_SESSION_PASSWORD)
        except NoSuchElementException:
            flash(l.ERR_LINKEDIN_LOGIN_WRONG)
            app.config['driver'].quit()
            return redirect(url_for('linklogin'))
        
        username.send_keys(usuario)
        password.send_keys(contrasena)
        app.config['driver'].find_element(By.XPATH, l.ELEMENT_BUTTON_SUBMIT).click()
        h.wait_random_time()

        # Si la URL a la que llego es la de inicio o la de nuevamente introducir login, es que las credenciales no son correctas
        if app.config['driver'].current_url == l.URL_LINKEDIN_LOGIN or app.config['driver'].current_url == l.URL_LINKEDIN_HOME:
            flash(l.ERR_LINKEDIN_LOGIN_WRONG)
            app.config['driver'].quit()
            return redirect(url_for('linklogin'))
        else:
            # Almaceno credenciales LinkedIn en sesión para sucesivas llamadas solo si el login fue correcto
            session['link_user'] = usuario
            session['link_pass'] = contrasena

            # Trato de recuperar el nombre propio del usuario; si no lo encuentra, muestro el email
            nombre_propio = ''
            try:
                nombre_propio = app.config['driver'].find_element(By.XPATH, l.PATH_WELCOME_NAME).text.split(' ')[0]
            except NoSuchElementException:
                nombre_propio = usuario
            return render_template('busqueda.html', usuario=nombre_propio)
    else:
        if session.get('user_id') is not None:
            return render_template('linklogin.html')
        else:
            return render_template('index.html')



@app.route('/viewprofile', methods=['GET'])
@h.login_required
def viewprofile():
    return render_template('viewprofile.html')
        


##################################################################
def validate_shots(numero_shots):
    ''' 
    Valido el numero de shots introducido por el usuario.
    - Si deja el valor vacio, devuelvo el maximo de shots que tiene disponible.
    - Si introduce un valor, lo valido y devuelvo el valor correcto
    - Si da un error, se valida como "not number"
    '''
    if session.get('opcion') == '1':
        if numero_shots.strip() == '':
            return session.get('visits_left', 0)
        else:
            return h.check_number(request.form.get('numero_shots'), session.get('visits_left', 0))
    elif session.get('opcion') == '2':
        if numero_shots.strip() == '':
            return session.get('messages_left', 0)
        else:
            return h.check_number(request.form.get('numero_shots'), session.get('messages_left', 0))
    elif session.get('opcion') == '3':
        if numero_shots.strip() == '':
            return session.get('connections_left', 0)
        else:
            return h.check_number(request.form.get('numero_shots'), session.get('connections_left', 0))
##################################################################
        


##################################################################
def async_scrapping(shots, deep, cuadro_texto, opcion):
    '''
    Realizo el scrapeo como tal, recorriendo páginas de resultados.
    Se ejecutará en un hilo asíncrono para no bloquear la aplicación.
    '''
    # Empiezo a contar el tiempo
    start = time.time()
    end = 0.0
    
    # Obtengo cantidad de resultados y calculo numero de paginas
    str_results = app.config['driver'].find_element(By.XPATH, l.PATH_NUMBER_RESULTS)
    num_pags = h.number_of_pages(str_results)
    # "shots" me da una idea de cuántas páginas como mucho voy a recorrer
    pages_shot = ceil(shots / 10)

    # Acoto a 100 el numero maximo de paginas a visitar porque LinkedIn no permirte visualizar más
    if num_pags > l.MAX_RESULT_PAGES:
        num_pags = l.MAX_RESULT_PAGES

    
    # Comienzo bucle externo. Si he llegado aquí, siempre debería encontrar al menos 1 página.
    pagina = 1
    # El bucle externo se detiene en la última página o si se ha alcanzado el tope de shots definido
    while (pagina <= num_pags and pagina <= pages_shot):

        # Recargo la pagina de busqueda y espero un poco
        app.config['driver'].get(l.URL_LINKEDIN_SEARCH_PEOPLE + cuadro_texto + deep + f"&page={pagina}")
        
        # DEBUG
        # app.config['driver'].get(f"{carlos}&page={pagina}")
        
        h.wait_random_time()

        # Construyo la lista de perfiles a visitar en esa pagina (LinkedIn muestra maximo 10 por cada una)
        profiles = app.config['driver'].find_elements(By.XPATH, l.ELEMENT_PAGE_PROFILES)
        visit_profiles = [p for p in profiles]
        # Itero sobre la lista de perfiles de cada pagina
        i = 1
        for p in visit_profiles:            
            try:
                # Guardo el enlace al perfil
                url = p.get_attribute('href')
                usuario = h.extract_username(url)
                public_url = h.build_public_url(usuario)
                
                # Si el perfil no es visible o accesible, estos elementos no existirían, por lo que se lanzaria otra excepcion, que capturo y salto al siguiente perfil
                nombre = app.config['driver'].find_element(By.XPATH, h.path_name(i)).text
                rol = app.config['driver'].find_element(By.XPATH, h.path_role(i)).text
                
                # DEBUG
                # print(f'El perfil de {nombre} se titula "{rol}" y su url es {public_url}')

                # Agrego el contacto a la lista
                contacto = h.Persona(nombre, rol, url, public_url, None)
                # Solo si la opcion es enviar mensajes, recupero el mensaje y lo añado a la Persona
                if opcion == '2':
                    custom_message = app.config['texto_mensaje'].replace('----', nombre.split(' ')[0])
                    contacto.set_mensaje(custom_message)
                    app.config['perfiles_visitados'].append(contacto)
                
            except NoSuchElementException:
                # Si caigo aquí, es porque el perfil no es visible o accesible ("Miembro de LinkedIn", perfil privado...), así que lo omito y paso al próximo
                i += 1
                pass
            finally:
                i += 1
                h.wait_random_time()

        # Si tengo que conectar o enviar mensajes, no he visitado perfil (aunque haya recuperado sus datos).
        if opcion == '3':
            # Construyo la lista de botones "Conectar" en cada una de las paginas
            all_buttons = app.config['driver'].find_elements(By.TAG_NAME, "button")
            connect_buttons = [btn for btn in all_buttons if btn.text == l.ELEMENT_BUTTON_CONNECT]
            for btn in connect_buttons:
                app.config['driver'].execute_script("arguments[0].click();", btn)
                h.wait_random_time()
                send = app.config['driver'].find_element(By.XPATH, l.ELEMENT_BUTTON_SEND_NOW)
                app.config['driver'].execute_script("arguments[0].click();", send)
                # TODO: conseguir saltar a contactos con mayor nivel de privacidad
        '''
        elif opcion == '2':
            message_buttons = app.config['driver'].find_elements(By.XPATH, "//button[contains(@aria-label, 'Enviar mensaje')]")

            for btn in message_buttons:
                # Click en el boton de mandar el mensaje y esperar un poco
                app.config['driver'].execute_script("arguments[0].click();", btn)
                h.wait_random_time()
                # Conseguir el nombre del destinatario y personalizar el mensaje
                name = btn.get_attribute('aria-label').split(' ')[3]
                custom_message = app.config['texto_mensaje'].replace('----', name)
                # TODO: aquí, añadir mensaje a clase Persona


                # Encuentro el 'div' en el que está el párrafo que contendrá el texto, y encuentro el párrafo
                # app.config['driver'].find_element(By.XPATH, "//div[starts-with(@class, 'msg-form__msg-content-container')]").click()
                # textfields = app.config['driver'].find_elements(By.TAG_NAME, "p")
                
                # Borro el cuadro de texto, que por defecto ocupa 2 párrafos
                # textfields[-6].clear()
                # textfields[-5].clear()
                # En el párrafo que queda, escribo el mensaje personalizado y vuelvo a esperar
                # textfields[-5].send_keys(custom_message)
                
                # TODO: ojo, este es un punto critico!!!!
                # Hago click en enviar
                # send_button = app.config['driver'].find_element(By.XPATH, "//button[starts-with(@class, 'msg-form__send-button')]")
                # app.config['driver'].execute_script("arguments[0].click();", send_button)
                
                # Busco darle a intro en el cuadro de texto, pero para eso hay que tener configurado antes eso en el LinkedIn de cada cual.
                # textfields[-5].send_keys(Keys.RETURN)

                # Hago click en cerrar la ventanita del mensaje y espero
                close_window_msg = app.config['driver'].find_element(By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')]")
                app.config['driver'].execute_script("arguments[0].click();", close_window_msg)
                h.wait_random_time()
        '''
        pagina += 1
    
    # Ya tengo construida la lista de personas a quienes he visitado el perfil, enviado mensaje o solicitado conexion. Ahora, les visito el perfil::
    '''
    if opcion == '1':
        for person in app.config['perfiles_visitados']:
            app.config['driver'].get(person.url)
            h.wait_random_time()
    '''
    # Paro el reloj, cierro el scrapper
    end = time.time()
    app.config['driver'].quit()
    app.config['tiempo'] = h.parse_time(round(end - start, 2))

    # DEBUG
    print("Codigo asincrono ejecutado")
    
    return
##################################################################



@app.route('/busqueda', methods=['POST', 'GET'])
@h.login_required
def busqueda():
    '''
    1. Recupero la opción y en base a ella ejecuto unas u otras funciones
    2. Recupero el texto de busqueda y realizo la busqueda 
    '''
    if request.method == 'POST':   
        # Si el usuario no especifica cuántos shots quiere gastar, por defecto le doy el máximo de los que dispone en cada tipo de accion:
        cuadro_texto = request.form.get('texto_busqueda')
        numero_shots = request.form.get('numero_shots')

        shots = validate_shots(numero_shots)

        if session.get('opcion') == '1':
            # Visitar perfiles: a contactos de segundo y tercer grado
            deep = l.DEEP_2_3
            if not shots:
                flash(l.ERR_NUMERICAL_SHOTS + session.get('visits_left', 0))
                return redirect(url_for('busqueda'))
            elif shots > int(session.get('visits_left', 0)):
                flash(l.ERR_NO_SHOTS_LEFT)
                return redirect(url_for('busqueda'))
        elif session.get('opcion') == '2':
            # Enviar mensajes solo a contactos de primer grado
            deep = l.DEEP_1
            if not shots:
                flash(l.ERR_NUMERICAL_SHOTS + session.get('messages_left', 0))
                return redirect(url_for('busqueda'))
            elif shots > int(session.get('messages_left', 0)):
                flash(l.ERR_NO_SHOTS_LEFT)
                return redirect(url_for('busqueda'))
        elif session.get('opcion') == '3':
            # Solicitud de conexion: solo a contactos de segundo grado
            deep = l.DEEP_2
            if not shots:
                flash(l.ERR_NUMERICAL_SHOTS + session.get('connections_left', 0))
                return redirect(url_for('busqueda'))
            elif shots > int(session.get('connections_left', 0)):
                flash(l.ERR_NO_SHOTS_LEFT)
                return redirect(url_for('busqueda'))
        
        # Reseteo los perfiles visitados en sesion en cada nueva busqueda
        app.config['perfiles_visitados'] = []

        # Cargo pagina de busqueda para averiguar cuantas vueltas daran los bucles, y si el usuario ha agotado sus visitas gratuitas en LinkedIn
        app.config['driver'].get(l.URL_LINKEDIN_SEARCH_PEOPLE + cuadro_texto + deep)
        if session.get('opcion') == '2':
            try:
                # "¿Quieres probar Sales Navigator por 0€?"
                app.config['driver'].find_element(By.XPATH, '//*[contains(@class,"artdeco-button--premium artdeco-button--secondary  premium-upsell-link--extra-long")]')
                flash("Se han agotado las búsquedas gratuitas. Revisa tu configuración de LinkedIn")
                app.config['tiempo'] = '(sin resultados)'
                app.config['driver'].quit()
                return render_template("done.html")
            except NoSuchElementException:
                pass
        else:
            try:
                # "¿Quieres probar Premium gratis durante un mes?"
                app.config['driver'].find_element(By.XPATH, '//*[contains(@class, "artdeco-button artdeco-button--premium artdeco-button--primary")]')
                flash("Se han agotado las búsquedas gratuitas. Revisa tu configuración de LinkedIn")
                app.config['tiempo'] = '(sin resultados)'
                app.config['driver'].quit()
                return render_template("done.html")
            except NoSuchElementException:
                pass
        
        # DEBUG: solo para buscar empresas concretas
        # app.config['driver'].get("https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22105646813%22%5D&keywords=logistica&origin=FACETED_SEARCH&sid=Yo-")
        # app.config['driver'].get("https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22105646813%22%5D&keywords=mensajeria&origin=GLOBAL_SEARCH_HEADER&sid=PzZ")
        # carlos = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22105646813%22%5D&industry=%5B%22135%22%2C%2253%22%2C%2223%22%2C%22112%22%2C%22147%22%2C%2218%22%2C%2260%22%5D&origin=FACETED_SEARCH&sid=B5L"
        # app.config['driver'].get(carlos)


        try:
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el 'empty-state';
            app.config['driver'].find_element(By.XPATH, l.ELEMENT_EMPTY_STATE)
            app.config['tiempo'] = '(sin resultados)'
            return render_template('done.html')
        except NoSuchElementException:
            session['shots'] = shots
            session['deep'] = deep
            session['cuadro_texto'] = cuadro_texto
            return render_template('confirm.html')

    else:
        if session.get('user_id') is not None:
            return render_template('busqueda.html')
        else:
            app.config['driver'].quit()
            return render_template('index.html')
        


@app.route('/check_status')
def check_status():
    '''
    Compruebo si el hilo de scrapping sigue ejecutándose o no
    '''
    if app.config['scrapping'].is_alive():
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'finished'})



@app.route('/confirm', methods=['POST'])
def confirm():
    '''
    Página de confirmación de la busqueda
    '''
    # DEBUG
    print("***********Voy a iniciar el hilo asincrono")
    # El scrapping va en un hilo asincrono para no bloquear la aplicación
    
    app.config['scrapping'] = Thread(target=async_scrapping, args=[session.get('shots'), session.get('deep'), session.get('cuadro_texto'), session.get('opcion')], daemon = True)
    app.config['scrapping'].start()

    # DEBUG
    print("***********Hilo asincrono iniciado")

    return url_for('wait')



@app.route('/wait')
def wait():
    # DEBUG
    print("Cargo la pagina de espera")
    return render_template('wait.html')



@app.route('/done', methods=['GET'])
def done():
    # Actualizo shots restantes en BD y muestro resultados
    shots_gastados = len(app.config['perfiles_visitados'])
    if session.get('opcion') == '1':
        session['visits_left'] = int(session.get('visits_left', 0)) - shots_gastados
        db.set_visits_left_by_id(int(session.get('visits_left', 0)), session["user_id"] )
    elif session.get('opcion') == '2':
        session['messages_left'] = int(session.get('messages_left', 0)) - shots_gastados
        db.set_messages_left_by_id(int(session.get('messages_left', 0)), session["user_id"] )
    elif session.get('opcion') == '3':
        session['connections_left'] = int(session.get('connections_left', 0)) - shots_gastados
        db.set_connections_left_by_id(int(session.get('connections_left', 0)), session["user_id"] )
    
    return render_template("done.html", numero_perfiles=shots_gastados)



@app.route('/descargar', methods=['POST', 'GET'])
@h.login_required
def descargar():
    ''' Descarga el archivo CSV con la información de los perfiles sobre los que se ha actuado '''
    
    with open(l.OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nombre', 'Rol', 'URL publica', 'Fecha de visita', 'Accion', 'Mensaje'])
        if session.get('opcion') == '1':
            accion = l.ACTION_PROFILE_VISITED
        elif session.get('opcion') == '2':
            accion = l.ACTION_MESSAGE_WRITTEN
        elif session.get('opcion') == '3':
            accion = l.ACTION_CONNECTION_SENT
        for perfil in app.config['perfiles_visitados']:
            writer.writerow([perfil.get_nombre(), perfil.get_rol(), perfil.get_public_url(), datetime.now().date(), accion, perfil.get_mensaje()])
    return send_file(l.OUTPUT_CSV, as_attachment=True)



if __name__ == '__main__':
    app.run()

