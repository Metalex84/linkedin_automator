from flask import Flask, render_template, request, session, url_for, redirect
from flask_session import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import random
import time

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

current_year = datetime.now().year
app.config['opcion'] = None
app.config['driver'] = None

@app.route('/')
def index():
    session.clear()
    app.config['driver'] = webdriver.Chrome()
    return render_template('index.html', current_year=current_year)


@app.route('/acciones', methods=['POST', 'GET'])
def acciones():
    accion = ''
    app.config['opcion'] = request.form.get('opciones')
    opt = app.config['opcion']
    if opt == '1':
        accion = 'visitar perfiles'
    elif opt == '2':
        accion = 'escribir mensajes'
    elif opt == '3':
        accion = 'enviar invitaciones'

    return render_template('login.html', current_year=current_year, accion=accion)


@app.route('/login', methods=['POST', 'GET'])
def login():
    usuario = request.form.get('username')
    contrasena = request.form.get('password')
    # Abro el navegador con LinkedIn
    app.config['driver'].get('https://www.linkedin.com')
    # Busco los campos de usuario y contraseña para meter los mios
    username = app.config['driver'].find_element(By.XPATH, '//*[@id="session_key"]')
    password = app.config['driver'].find_element(By.XPATH, '//*[@id="session_password"]')
    username.send_keys(usuario)
    password.send_keys(contrasena)
    # Busco el boton de submit para enviar el formulario web
    submit = app.config['driver'].find_element(By.XPATH, '//button[@type="submit"]')
    submit.click()
    time.sleep(random.randint(1, 4))
    return render_template('busqueda.html', usuario=usuario, current_year=current_year)


@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():
    time.sleep(random.randint(1, 4))
    # OJO: implementar opcion de busqueda avanzada: contactos de 2 o 3 grado, ubicacion, 
    opt = app.config['opcion']
    if opt == '1':
        # Voy a intentar averiguar cuántas páginas de resultados se producen. Me lo dirá el contenido del último button de la 'ul'...
        '''
        ESTO TODAVÍA NO SALE
        '''
        pagina = 1
        lista_raiz = app.config['driver'].find_elements(By.XPATH, '//*[@class="artdeco-pagination__pages artdeco-pagination__pages--number"]')
        print(lista_raiz)
   

        app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={request.form.get('texto_busqueda')}&origin=SWITCH_SEARCH_VERTICAL&page={pagina}")
        profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
        visit_profiles = [p for p in profiles]
        # OJO: copiar el contenido de visit_profiles a una lista nueva para que no se pierda al cerrar el navegador
        for p in visit_profiles:
            p_url = p.get_attribute('href')
            app.config['driver'].execute_script(f"window.open('{p_url}');")
            # En cada iteracion se abre una nueva pestaña con el perfil de la persona pero con webdriver, no con JS
            # Utiliza otro webdriver: driver2.get(p_url)
            # OJO: implementar un tiempo aleatorio para que no se bloquee el navegador
            # app.config['driver'].close()
            time.sleep(random.randint(1, 4))
    
    elif opt == '2':
        print('Escribir mensajes no implementado aun')
        
    elif opt == '3':
        print('Enviar invitaciones no implementado aun')
        # Para conectar seria: driver.execute_script("arguments[0].click();", p)

    else:
        return render_template('index.html', current_year=current_year)

    app.config['driver'].close()
    session.clear()
    return render_template("done.html", profiles=visit_profiles, current_year=current_year)

    # Filtrado info de contacto (clasificado entre email corporativo o personal).


if __name__ == '__main__':
    app.run()


    '''
    Al final habrá que hacer un área privada con preferencias de cada cual, con mapeo de las visitas (quién está conectado), y que se guarden
    las preferencias de cada usuario (credenciales de Linkedin, preferencias de busqueda, rol en la empresa, fotos, etcétera).
    '''