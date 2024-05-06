from flask import Flask, flash, redirect, render_template, url_for, request, session, send_file
from flask_session import Session

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
import secrets
import time
import csv

import helpers as h
import model as db


''' Configuro la aplicacion Flask y la clave secreta '''
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)



''' Configuro la session para utilizar el sistema de archivos en lugar de cookies '''
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



''' Configuro variables globales'''
app.config['opcion'] = None
app.config['driver'] = None
app.config['texto_mensaje'] = None



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
        session['shots'] = user["shots"]
        return render_template('actions.html', current_year=datetime.now().year, username=user["usuario"], connection=user["connection"], shots=session['shots'])
        
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
            flash(h.ERR_NO_USERNAME)
            return redirect(url_for('index'))
        elif not request.form.get('password'):
            flash(h.ERR_NO_PASSWORD)
            return redirect(url_for('index'))
        
        user = db.get_user_by_name(request.form.get('username'))

        if len(user) != 1 or not check_password_hash(user[0]['password'], request.form.get('password')):
            flash(h.ERR_USER_OR_PASS_WRONG)
            return redirect(url_for('index'))

        # Guardo en sesión los datos que necesitaré del usuario mientras esté logueado
        session["user_id"] = user[0]['id']
        session["username"] = user[0]['usuario']
        session["shots"] = user[0]['shots']

        # Consulto la ultima fecha de conexion del usuario; si es anterior al dia actual, le reseteo los shots
        ultima_conexion = db.get_connection_by_id(session["user_id"])
        if ultima_conexion is not None:
            last_connect = datetime.strptime(ultima_conexion, h.DATE_FORMAT)            
            if last_connect.date() < datetime.now().date():
                db.set_shots_by_id(h.MAX_SHOTS, session["user_id"])

        return render_template("actions.html", current_year=datetime.now().year, username=request.form.get('username'))

    else:
        return render_template('index.html', current_year=datetime.now().year)



@app.route("/logout")
def logout():
    '''
    Cierro la sesion del usuario guardando la fecha y hora de la ultima conexion
    '''
    db.set_connection_by_id(datetime.now().strftime(h.DATE_FORMAT), session["user_id"])
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
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        cursor = db.get_user_by_name(username)

        if not username:
            flash(h.ERR_NO_USERNAME)
            return redirect(url_for('register'))
        elif len(cursor) != 0:
            flash(h.ERR_USER_ALREADY_EXISTS)
            return redirect(url_for('register'))
        elif not password:
            flash(h.ERR_NO_PASSWORD)
            return redirect(url_for('register'))
        elif not confirmation:
            flash(h.ERR_CONFIRM_PASSWORD)
            return redirect(url_for('register'))
        elif password != confirmation:
            flash(h.ERR_PASSWORDS_NOT_MATCH)
            return redirect(url_for('register'))
        elif not h.check_valid_username(username):
            flash(h.ERR_CORPORATE_EMAIL)
            return redirect(url_for('register'))
        else:
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.insert_user(username, hash, h.MAX_SHOTS)
            session["user_id"] = db.get_user_by_name(username)[0]['id']
            return redirect(url_for('acciones'))
    else:
        return render_template('register.html', current_year=datetime.now().year)



@app.route('/forgot', methods=['GET'])
def forgot():
    return render_template('reset.html', current_year=datetime.now().year)



@app.route('/reset', methods=['POST', 'GET'])
def reset():
    ''' Recojo la nueva contraseña y la confirmación, las comparo y actualizo la BD '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            flash(h.ERR_NO_USERNAME)
            return redirect(url_for('reset'))
        elif not password:
            flash(h.ERR_NO_NEW_PASSWORD)
            return redirect(url_for('reset'))
        elif not confirmation:
            flash(h.ERR_NO_CONFIRM_PASSWORD)
            return redirect(url_for('reset'))
        elif password != confirmation:
            flash(h.ERR_PASSWORDS_NOT_MATCH)
            return redirect(url_for('reset'))
        else:
            user = db.get_user_by_name(username)
            if len(user) != 1:
                flash(h.ERR_USER_ALREADY_EXISTS)
                return redirect(url_for('reset'))
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.set_password_by_id(hash, user[0]['id'])
            return redirect(url_for('index'))
    else:
        return render_template('reset.html', current_year=datetime.now().year)



@app.route('/acciones', methods=['POST', 'GET'])
@h.login_required
def acciones():
    '''
    1. Recojo la opción seleccionada por el usuario, solo si tiene acciones disponibles restantes
    2. Devuelvo la acción seleccionada en forma de texto
    '''
    user = db.get_user_by_id(session["user_id"])
    session['shots'] = user["shots"]
    if request.method == 'POST':
        session['accion'] = ''
        app.config['opcion'] = request.form.get('opciones')
        opt = app.config['opcion']
        if opt == '1':
            session['accion'] = h.ACTION_VISIT_PROFILES
        elif opt == '2':
            session['accion'] = h.ACTION_WRITE_MESSAGES
            # Recupero el texto del mensaje que deseo enviar
            app.config['texto_mensaje'] = request.form.get('mensaje')
            if not app.config['texto_mensaje']:
                flash(h.ERR_EMPTY_MESSAGE)
                return redirect(url_for('acciones'))
        elif opt == '3':
            session['accion'] = h.ACTION_SEND_CONNECTIONS
        return render_template('linklogin.html', current_year=datetime.now().year)
        
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
@h.login_required
def linklogin():
    '''
    1. Abro navegador, uso las claves de acceso de LinkedIn y redirijo a la página de busqueda
    2. Controlo posible fallo de login, devolviendo un mensaje de error
    '''
    if request.method == 'POST':
        # Si no tengo los datos cogidos desde la session, los recojo del formulario
        if not (session.get('link_user') and session.get('link_pass')):
            usuario = request.form.get('username')
            contrasena = request.form.get('password')

            if not usuario:
                flash(h.ERR_NO_LINKEDIN_USER)
                return redirect(url_for('linklogin'))
            elif not contrasena:
                flash(h.ERR_NO_LINKEDIN_PASS)
                return redirect(url_for('linklogin'))
        else:
            usuario = session.get('link_user')
            contrasena = session.get('link_pass')
        
        # Abro navegador y redirijo a la página de LinkedIn
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # app.config['driver'] = webdriver.Chrome(options=chrome_options)
        
        # app.config['driver'] =  webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=webdriver.FirefoxOptions())
        app.config['driver'] = webdriver.Firefox()
        app.config['driver'].get(h.URL_LINKEDIN_HOME)
        username = app.config['driver'].find_element(By.XPATH, h.ELEMENT_SESSION_KEY)
        password = app.config['driver'].find_element(By.XPATH, h.ELEMENT_SESSION_PASSWORD)
        username.send_keys(usuario)
        password.send_keys(contrasena)
        app.config['driver'].find_element(By.XPATH, h.ELEMENT_BUTTON_SUBMIT).click()
        h.wait_random_time()

        # Si la URL a la que llego es la de inicio o la de nuevamente introducir login, es que las credenciales no son correctas
        if app.config['driver'].current_url == h.URL_LINKEDIN_LOGIN or app.config['driver'].current_url == h.URL_LINKEDIN_HOME:
            flash(h.ERR_LINKEDIN_LOGIN_WRONG)
            app.config['driver'].quit()
            return redirect(url_for('linklogin'))
        else:
            # Almaceno credenciales LinkedIn en sesión para sucesivas llamadas solo si el login fue correcto
            session['link_user'] = usuario
            session['link_pass'] = contrasena
            nombre_propio = ''
            try:
                nombre_propio = app.config['driver'].find_element(By.XPATH, h.PATH_WELCOME_NAME).text.split(' ')[0]
            except NoSuchElementException:
                nombre_propio = usuario
            return render_template('busqueda.html', usuario=nombre_propio, current_year=datetime.now().year, remaining_shots=session.get('shots', 0))
    else:
        if session.get('user_id') is not None:
            return render_template('linklogin.html', current_year=datetime.now().year)
        else:
            return render_template('index.html', current_year=datetime.now().year)



@app.route('/viewprofile', methods=['GET'])
@h.login_required
def viewprofile():
    username = db.get_user_by_id(session["user_id"])
    return render_template('viewprofile.html', current_year=datetime.now().year, username=username["usuario"], connection=username["connection"], shots=username["shots"])
        


@app.route('/busqueda', methods=['POST', 'GET'])
@h.login_required
def busqueda():
    '''
    1. Recupero la opción y en base a ella ejecuto unas u otras funciones
    2. Recupero el texto de busqueda y realizo la busqueda 
    '''
    if request.method == 'POST':   
        # Si el usuario no especifica cuántos shots quiere gastar, por defecto le doy el máximo de los que dispone
        numero_shots = request.form.get('numero_shots')
        if numero_shots.strip() == '':
            # TODO: Emitir alerta modal JS para que el usuario se pueda echar atrás, hacerlo desde el lado del cliente
            numero_shots = int(session.get('shots', 0))
        else:
            # Valido si el dato introducido está en los límites, es un entero positivo, etc
            numero_shots = h.check_number(request.form.get('numero_shots'), session.get('shots', 0))
            if not numero_shots:
                flash(h.ERR_NUMERICAL_SHOTS + session.get('shots', 0))
                # flash(f'¡Introduce un número entero entre 1 y {session.get('shots', 0)}!')
                return redirect(url_for('busqueda'))
            
        # Si el número de shots que el usuario pide hacer es mayor que los que tiene disponibles, le devuelvo un mensaje de error
        if numero_shots > int(session.get('shots', 0)):
            flash(h.ERR_NO_SHOTS_LEFT)
            return redirect(url_for('busqueda'))
        
        # Reseteo los perfiles visitados en sesion en cada nueva busqueda
        session['perfiles_visitados'] = []
        cuadro_texto = request.form.get('texto_busqueda')
        opt = app.config['opcion']

        # Discrimino profundidad en base a opcion
        if opt == '1':
            # Visitar perfiles: a contactos de segundo y tercer grado
            deep = h.DEEP_2_3
        elif opt == '2':
            # Enviar mensajes solo a contactos de primer grado
            deep = h.DEEP_1
        elif opt == '3':
            # Solicitud de conexion: solo a contactos de segundo grado
            deep = h.DEEP_2

        # Cargo pagina de busqueda para averiguar cuantas vueltas daran los bucles
        app.config['driver'].get(h.URL_LINKEDIN_SEARCH_PEOPLE + cuadro_texto + deep)
        
        # DEBUG: solo para buscar empresas concretas
        # app.config['driver'].get("https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22105646813%22%5D&keywords=logistica&origin=FACETED_SEARCH&sid=Yo-")
        # app.config['driver'].get("https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22105646813%22%5D&keywords=mensajeria&origin=GLOBAL_SEARCH_HEADER&sid=PzZ")
        # carlos = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22105646813%22%5D&industry=%5B%22135%22%2C%2253%22%2C%2223%22%2C%22112%22%2C%22147%22%2C%2218%22%2C%2260%22%5D&origin=FACETED_SEARCH&sid=B5L"
        # app.config['driver'].get(carlos)

        # Empiezo a contar el tiempo
        start = time.time()
        end = 0.0

        try:
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el 'empty-state';
            app.config['driver'].find_element(By.XPATH, h.ELEMENT_EMPTY_STATE)
            return render_template("done.html", profiles=session['perfiles_visitados'], current_year=datetime.now().year, tiempo='(sin resultados)')
        except NoSuchElementException:
            # Obtengo cantidad de resultados y calculo numero de paginas
            str_results = app.config['driver'].find_element(By.XPATH, h.PATH_NUMBER_RESULTS)
            num_pags = h.number_of_pages(str_results)
            # Acoto a 100 el numero maximo de paginas a visitar por seguridad
            if num_pags >= int(h.MAX_RESULT_PAGES):
                num_pags = int(h.MAX_RESULT_PAGES)
        
            # Comienzo bucle externo. Si he llegado aquí, siempre debería encontrar al menos 1 página.
            pagina = 1
            # El bucle externo se detiene si se han visitado todos los perfiles, si se ha alcanzado el tope de shots definido, o hasta la página 100
            while (pagina <= num_pags and len(session['perfiles_visitados']) < numero_shots):  
                # Recargo la pagina de busqueda y espero un poco
                app.config['driver'].get(h.URL_LINKEDIN_SEARCH_PEOPLE + cuadro_texto + deep + f"&page={pagina}")
                
                #
                # app.config['driver'].get(f"{carlos}&page={pagina}")
                #
                
                h.wait_random_time()
                # Construyo la lista de perfiles a visitar en esa pagina (LinkedIn muestra maximo 10 por cada una)
                profiles = app.config['driver'].find_elements(By.XPATH, h.ELEMENT_PAGE_PROFILES)
                visit_profiles = [p for p in profiles]
                # Itero sobre la lista de perfiles de cada pagina
                i = 1
                for p in visit_profiles:
                    try:
                        # Si 'p' fuese un "Miembro de LinkedIn", estos elementos no existirían, por lo que se lanzaria otra excepcion, que capturo y salto al siguiente perfil
                        nombre = app.config['driver'].find_element(By.XPATH, h.path_name(i)).text
                        rol = app.config['driver'].find_element(By.XPATH, h.path_role(i)).text
                        
                        # Guardo tambien el enlace al perfil
                        p_url = p.get_attribute('href')
                        
                        # Puede que más adelante necesite hacer algo con el nombre de usuario de LinkedIn de cada contacto
                        usuario = h.extract_username(p_url)

                        # DEBUG
                        print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        #
                        
                        # Agrego el contacto a la lista
                        contacto = h.Persona(nombre, rol, p_url)
                        session['perfiles_visitados'].append(contacto)

                    except NoSuchElementException:
                        pass
                    finally:
                        i += 1
                        h.wait_random_time()

                # Si tengo que conectar o enviar mensajes, no he visitado perfil (aunque haya recuperado sus datos).
                if opt == '3':
                    # Construyo la lista de botones "Conectar" en cada una de las paginas
                    all_buttons = app.config['driver'].find_elements(By.TAG_NAME, "button")
                    connect_buttons = [btn for btn in all_buttons if btn.text == h.ELEMENT_BUTTON_CONNECT]
                    for btn in connect_buttons:
                        app.config['driver'].execute_script("arguments[0].click();", btn)
                        h.wait_random_time()
                        send = app.config['driver'].find_element(By.XPATH, h.ELEMENT_BUTTON_SEND_NOW)
                        app.config['driver'].execute_script("arguments[0].click();", send)
                        # TODO: conseguir saltar a contactos con mayor nivel de privacidad

                elif opt == '2':
                    # TODO: ENVIO DE MENSAJES, no va a ser posible implementarlo asi
                    message_buttons = app.config['driver'].find_elements(By.XPATH, "//button[contains(@aria-label, 'Enviar mensaje')]")
                    for btn in message_buttons:
                        # Click en el boton de mandar el mensaje y esperar un poco
                        app.config['driver'].execute_script("arguments[0].click();", btn)
                        h.wait_random_time()
                        # Conseguir el nombre del destinatario y personalizar el mensaje
                        name = btn.get_attribute('aria-label').split(' ')[3]
                        custom_message = app.config['texto_mensaje'].replace('[[]]', name)
                        # Encuentro el 'div' en el que está el párrafo que contendrá el texto, y encuentro el párrafo
                        app.config['driver'].find_element(By.XPATH, "//div[starts-with(@class, 'msg-form__msg-content-container')]").click()
                        textfields = app.config['driver'].find_elements(By.TAG_NAME, "p")
                        # Borro el cuadro de texto, que por defecto ocupa 2 párrafos
                        # textfields[-6].clear()
                        # textfields[-5].clear()
                        # En el párrafo que queda, escribo el mensaje personalizado y vuelvo a esperar
                        textfields[-5].send_keys(custom_message)
                        
                        # TODO: ojo, este es un punto critico!!!!
                        # Hago click en enviar
                        # send_button = app.config['driver'].find_element(By.XPATH, "//button[starts-with(@class, 'msg-form__send-button')]")
                        # app.config['driver'].execute_script("arguments[0].click();", send_button)
                        
                        # Busco darle a intro en el cuadro de texto, pero para eso hay que tener configurado antes eso en el LinkedIn de cada cual.
                        textfields[-5].send_keys(Keys.RETURN)

                        # Hago click en cerrar la ventanita del mensaje y espero
                        close_window_msg = app.config['driver'].find_element(By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')]")
                        app.config['driver'].execute_script("arguments[0].click();", close_window_msg)
                        h.wait_random_time()
                pagina += 1
            
            # Ya tengo construida la lista de personas a quienes he visitado el perfil, enviado mensaje o solicitado conexion. Ahora, les visito el perfil::
            
            if opt == '1':
                for person in session['perfiles_visitados']:
                    app.config['driver'].get(person.url)
                    h.wait_random_time()
            
            # Paro el reloj, cierro el scrapper, actualizo shots restantes en BD y muestro resultados
            end = time.time()
            app.config['driver'].quit()
            shots_gastados = len(session['perfiles_visitados'])
            db.set_shots_by_id(int(session.get('shots', 0)) - shots_gastados, session["user_id"] )
            return render_template("done.html", profiles=session['perfiles_visitados'], current_year=datetime.now().year, tiempo=h.parse_time(round(end - start, 2)), numero_perfiles=shots_gastados)

    else:
        if session.get('user_id') is not None:
            return render_template('busqueda.html', usuario=session.get('link_user'), current_year=datetime.now().year, remaining_shots=session.get('shots', 0))
        else:
            app.config['driver'].quit()
            return render_template('index.html', current_year=datetime.now().year)
        


@app.route('/descargar', methods=['POST', 'GET'])
@h.login_required
def descargar():
    ''' Descarga el archivo CSV con la información de los perfiles sobre los que se ha actuado '''
    
    with open(h.OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nombre', 'Rol', 'URL', 'Fecha de visita', 'Accion'])
        if app.config['opcion'] == '1':
            accion = h.ACTION_PROFILE_VISITED
        elif app.config['opcion'] == '2':
            accion = h.ACTION_MESSAGE_WRITTEN
        elif app.config['opcion'] == '3':
            accion = h.ACTION_CONNECTION_SENT
        for perfil in session['perfiles_visitados']:
            writer.writerow([perfil.nombre, perfil.rol, perfil.url, datetime.now().date(), accion])
    return send_file(h.OUTPUT_CSV, as_attachment=True)



if __name__ == '__main__':
    app.run()

