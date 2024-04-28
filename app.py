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

from helpers import Persona, wait_random_time, parse_time, number_of_pages, login_required, extract_username, check_valid_username, check_number
import model as db


''' Configuro la aplicacion Flask y la clave secreta '''
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)



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
            flash('¡Introduce tu nombre de usuario!')
            return redirect('/')
        elif not request.form.get('password'):
            flash('¡Introduce tu contraseña!')
            return redirect('/')
        
        user = db.get_user_by_name(request.form.get('username'))

        if len(user) != 1 or not check_password_hash(user[0]['password'], request.form.get('password')):
            flash('¡Usuario o contraseña incorrectos!')
            return redirect('/')

        # Guardo el id de usuario para que persista el login        
        session["user_id"] = user[0]['id']

        # Consulto la ultima fecha de conexion del usuario; si es anterior al dia actual, le reseteo los shots
        ultima_conexion = db.get_connection_by_id(session["user_id"])
        if ultima_conexion is not None:
            last_connect = datetime.strptime(ultima_conexion, DATE_FORMAT)            
            if last_connect.date() < datetime.now().date():
                db.set_shots_by_id(MAX_SHOTS, session["user_id"])

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
            flash('¡Introduce un nombre de usuario!')
            return redirect(url_for('register'))
        elif len(cursor) != 0:
            flash('¡Este nombre de usuario ya existe!')
            return redirect(url_for('register'))
        elif not password:
            flash('¡Introduce una contraseña!')
            return redirect(url_for('register'))
        elif not confirmation:
            flash('¡Confirma tu contraseña!')
            return redirect(url_for('register'))
        elif password != confirmation:
            flash('¡Las contraseñas no coinciden!')
            return redirect(url_for('register'))
        elif not check_valid_username(username):
            flash('¡Utiliza tu correo corporativo como nombre de usuario!')
            return redirect(url_for('register'))
        else:
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.insert_user(username, hash, MAX_SHOTS)
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
            flash('¡Introduce tu nombre de usuario!')
            return redirect(url_for('reset'))
        elif not password:
            flash('¡Introduce una nueva contraseña!')
            return redirect(url_for('reset'))
        elif not confirmation:
            flash('¡Confirma tu nueva contraseña!')
            return redirect(url_for('reset'))
        elif password != confirmation:
            flash('¡Las contraseñas no coinciden!')
            return redirect(url_for('reset'))
        else:
            user = db.get_user_by_name(username)
            if len(user) != 1:
                flash('¡Hay más de un usuario con el mismo login! Contacta con el administrador del sistema')
                return redirect(url_for('reset'))
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
            db.set_password_by_id(hash, user[0]['id'])
            return redirect(url_for('index'))
    else:
        return render_template('reset.html', current_year=datetime.now().year)



@app.route('/acciones', methods=['POST', 'GET'])
@login_required
def acciones():
    '''
    1. Recojo la opción seleccionada por el usuario, solo si tiene acciones disponibles restantes
    2. Devuelvo la acción seleccionada en forma de texto
    '''
    user = db.get_user_by_id(session["user_id"])
    session['shots'] = user["shots"]
    if request.method == 'POST':
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
                flash('¡Introduce un mensaje!')
                return redirect(url_for('actions'))
        elif opt == '3':
            accion = 'enviar invitaciones'
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
        # Si no tengo los datos cogidos desde la session, los recojo del formulario
        if not (session.get('link_user') and session.get('link_pass')):
            usuario = request.form.get('username')
            contrasena = request.form.get('password')

            if not usuario:
                flash('¡Introduce tu usuario de LinkedIn!')
                return redirect(url_for('linklogin'))
            elif not contrasena:
                flash('¡Introduce tu contraseña de LinkedIn!')
                return redirect(url_for('linklogin'))
        else:
            usuario = session.get('link_user')
            contrasena = session.get('link_pass')
        
        # Almaceno credenciales LinkedIn en sesión para sucesivas llamadas
        session['link_user'] = usuario
        session['link_pass'] = contrasena

        # Abro navegador y redirijo a la página de LinkedIn
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # app.config['driver'] = webdriver.Chrome(options=chrome_options)
        
        # app.config['driver'] =  webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=webdriver.FirefoxOptions())
        app.config['driver'] = webdriver.Firefox()

        app.config['driver'].get('https://www.linkedin.com')
        username = app.config['driver'].find_element(By.XPATH, '//*[@id="session_key"]')
        password = app.config['driver'].find_element(By.XPATH, '//*[@id="session_password"]')
        username.send_keys(session.get('link_user'))
        password.send_keys(session.get('link_pass'))
        app.config['driver'].find_element(By.XPATH, '//button[@type="submit"]').click()
        wait_random_time()

        if app.config['driver'].current_url == 'https://www.linkedin.com/uas/login-submit':
            flash('¡Usuario o contraseña de LinkedIn incorrectos!')
            return redirect(url_for('linklogin'))
        else:
            return render_template('busqueda.html', usuario=usuario, current_year=datetime.now().year, remaining_shots=session.get('shots', 0))
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
        if int(request.form.get('numero_shots')) > session.get('shots', 0):
            flash('¡No tienes suficientes acciones restantes!')
            return redirect(url_for('busqueda'))
        # Reseteo los perfiles visitados en sesion en cada nueva busqueda
        session['perfiles_visitados'] = []
        cuadro_texto = request.form.get('texto_busqueda')
        opt = app.config['opcion']

        # Discrimino profundidad en base a opcion
        if opt == '1':
            # Visitar perfiles: a contactos de segundo y tercer grado
            deep = '&network=%5B"S"%2C"O"%5D'
        elif opt == '2':
            # Enviar mensajes solo a contactos de primer grado
            deep = '&network=%5B"F"%5D'
        elif opt == '3':
            # Solicitud de conexion: solo a contactos de segundo grado
            deep = '&network=%5B"S"%5D'

        # Cargo pagina de busqueda para averiguar cuantas vueltas daran los bucles
        app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")

        # Empiezo a contar el tiempo
        start = time.time()
        end = 0.0

        try:
            # Si la busqueda ha producido resultados se lanzará una excepción porque no encontraré el 'empty-state';
            app.config['driver'].find_element(By.XPATH, '//h2[contains(@class, "artdeco-empty-state__headline")]')
            return render_template("done.html", profiles=session['perfiles_visitados'], current_year=datetime.now().year, tiempo='(sin resultados)')
        except NoSuchElementException:
            # Obtengo cantidad de resultados y calculo numero de paginas
            str_results = app.config['driver'].find_element(By.XPATH, '//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2')
            num_pags = number_of_pages(str_results)

            maximum_shots = check_number(request.form.get('numero_shots'))

            # TODO: escribir lógica de control (qué hago si este número no es correcto)

            # Comienzo bucle externo. Si he llegado aquí, siempre debería encontrar al menos 1 página.
            pagina = 1
            # No rebasar los shots restantes es una condición complementaria de parada
            while pagina <= num_pags and len(session['perfiles_visitados']) < maximum_shots:  
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
                        # Si 'p' fuese un "Miembro de LinkedIn", estos elementos no existirían, por lo que se lanzaria otra excepcion, que capturo y salto al siguiente perfil
                        path_name = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[1]/div/span[1]/span/a/span/span[1]"
                        path_role = f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[2]"
                        nombre = app.config['driver'].find_element(By.XPATH, path_name).text
                        rol = app.config['driver'].find_element(By.XPATH, path_role).text
                        
                        # Guardo tambien el enlace al perfil
                        p_url = p.get_attribute('href')
                        
                        # Puede que más adelante necesite hacer algo con el nombre de usuario de LinkedIn de cada contacto
                        usuario = extract_username(p_url)

                        # DEBUG
                        print(f'El perfil de {nombre}, {rol} se identifica como {usuario}')
                        #
                        
                        # Agrego el contacto a la lista
                        contacto = Persona(nombre, rol, p_url)
                        session['perfiles_visitados'].append(contacto)

                    except NoSuchElementException:
                        pass
                    finally:
                        i += 1
                        wait_random_time()

                # Si tengo que conectar o enviar mensajes, no he visitado perfil (aunque haya recuperado sus datos).
                if opt == '3':
                    # Construyo la lista de botones "Conectar" en cada una de las paginas
                    all_buttons = app.config['driver'].find_elements(By.TAG_NAME, "button")
                    connect_buttons = [btn for btn in all_buttons if btn.text == "Conectar"]
                    for btn in connect_buttons:
                        app.config['driver'].execute_script("arguments[0].click();", btn)
                        wait_random_time()
                        send = app.config['driver'].find_element(By.XPATH, "//button[@aria-label='Enviar ahora']")
                        app.config['driver'].execute_script("arguments[0].click();", send)
                        # TODO: conseguir saltar a contactos con mayor nivel de privacidad

                elif opt == '2':
                    # ENVIO DE MENSAJES
                    message_buttons = app.config['driver'].find_elements(By.XPATH, "//button[contains(@aria-label, 'Enviar mensaje')]")
                    for btn in message_buttons:
                        # Click en el boton de mandar el mensaje y esperar un poco
                        app.config['driver'].execute_script("arguments[0].click();", btn)
                        wait_random_time()
                        # Conseguir el nombre del destinatario y personalizar el mensaje
                        name = btn.get_attribute('aria-label').split(' ')[3]
                        custom_message = app.config['texto_mensaje'].replace('[[]]', name)
                        # Encuentro el 'div' en el que está el párrafo que contendrá el texto, y encuentro el párrafo
                        app.config['driver'].find_element(By.XPATH, "//div[starts-with(@class, 'msg-form__msg-content-container')]").click()
                        textfields = app.config['driver'].find_elements(By.TAG_NAME, "p")
                        # Borro el cuadro de texto, que por defecto ocupa 2 párrafos
                        textfields[-6].clear()
                        textfields[-5].clear()
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
                        wait_random_time()
                pagina += 1
            
            # Ya tengo construida la lista de personas a quienes he visitado el perfil, enviado mensaje o solicitado conexion:
            if opt == '1':
                for person in session['perfiles_visitados']:
                    app.config['driver'].get(person.url)
                    wait_random_time()

            # Paro el reloj, cierro el scrapper, actualizo shots restantes en BD y muestro resultados
            end = time.time()
            app.config['driver'].quit()
            shots_gastados = len(session['perfiles_visitados'])
            db.set_shots_by_id(int(session.get('shots', 0)) - shots_gastados, session["user_id"] )
            return render_template("done.html", profiles=session['perfiles_visitados'], current_year=datetime.now().year, tiempo=parse_time(round(end - start, 2)), numero_perfiles=shots_gastados)

    else:
        app.config['driver'].quit()
        return render_template('index.html', current_year=datetime.now().year)



@app.route('/descargar', methods=['POST', 'GET'])
@login_required
def descargar():
    ''' Descarga el archivo CSV con la información de los perfiles sobre los que se ha actuado '''
    ruta = 'perfiles.csv'
    with open('perfiles.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nombre', 'Rol', 'URL', 'Fecha de visita', 'Accion'])
        if app.config['opcion'] == '1':
            accion = 'Perfil visitado'
        elif app.config['opcion'] == '2':
            accion = 'Mensaje enviado'
        elif app.config['opcion'] == '3':
            accion = 'Solicitud de conexión'
        for perfil in session['perfiles_visitados']:
            writer.writerow([perfil.nombre, perfil.rol, perfil.url, datetime.now().date(), accion])
    return send_file(ruta, as_attachment=True)



if __name__ == '__main__':
    app.run()

