from flask import Flask, render_template, request, url_for, redirect
from flask_session import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
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
    # TODO: Implementar un selector para permitir al usuario elegir con qué navegador local quiere hacer el scrapping
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
    app.config['driver'].get('https://www.linkedin.com')
    username = app.config['driver'].find_element(By.XPATH, '//*[@id="session_key"]')
    password = app.config['driver'].find_element(By.XPATH, '//*[@id="session_password"]')
    username.send_keys(usuario)
    password.send_keys(contrasena)
    submit = app.config['driver'].find_element(By.XPATH, '//button[@type="submit"]')
    submit.click()
    time.sleep(random.randint(1, 4))
    return render_template('busqueda.html', usuario=usuario, current_year=current_year)


@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():
    # TODO:  
    # - opcion de busqueda avanzada: contactos de 2 o 3 grado, ubicacion...
    # - filtrado info de contacto (clasificado entre email corporativo o personal).
    opt = app.config['opcion']
    perfiles_visitados = []
    cuadro_texto = request.form.get('texto_busqueda')
    if opt == '1':
        pagina = 1
        app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}&origin=SWITCH_SEARCH_VERTICAL")
        while True:
            try:
                if not app.config['driver'].find_elements(By.CLASS_NAME, 'artdeco-empty-state__message'):
                    profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                    visit_profiles = [p for p in profiles]
                    # perfiles = visit_profiles[:]
                    # ¿Haría falta copiar el contenido de visit_profiles a una lista nueva para que no se pierda al cerrar el navegador?
                    # for p in perfiles:
                    for p in visit_profiles:
                        p_url = p.get_attribute('href')
                        app.config['driver'].execute_script(f"window.open('{p_url}');")
                        # TODO: recuperar informacion del perfil visitado e ir construyendo lista tras cada vuelta
                        perfiles_visitados.append(p)
                        '''
                        app.config['driver'].switch_to.window(app.config['driver'].window_handles[1])
                        app.config['driver'].close()
                        app.config['driver'].switch_to.window(app.config['driver'].window_handles[0])
                        '''
                        time.sleep(random.randint(1, 4))
                pagina += 1
                app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}&origin=SWITCH_SEARCH_VERTICAL&page={pagina}")
            except NoSuchElementException:
            # TODO: intentar cerrar todas las pestañas tras cada vuelta del bucle externo
                break
            app.config['driver'].quit() # Quizá no haga falta cerrar esto ahora, sino esperar a la ultima pantalla
            return render_template("done.html", profiles=perfiles_visitados, current_year=current_year)

    elif opt == '2':
        app.config['driver'].quit()
        return('Escribir mensajes no implementado aun')
        # TODO
        
    elif opt == '3':
        app.config['driver'].quit()
        return('Enviar invitaciones no implementado aun')
        # Para conectar seria: driver.execute_script("arguments[0].click();", p)
        # TODO

    else:
        app.config['driver'].quit()
        return('Aqui ha pasado algo raro...')


if __name__ == '__main__':
    app.run()


    '''
    Al final habrá que hacer un área privada con preferencias de cada cual, con mapeo de las visitas (quién está conectado), y que se guarden
    las preferencias de cada usuario (credenciales de Linkedin, preferencias de busqueda, rol en la empresa, fotos, etcétera).
    '''