from flask import Flask, render_template, request, url_for, redirect
from flask_session import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from linkedin_api import Linkedin
from urllib.parse import urlparse
from datetime import datetime
import random
import time
import csv

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

current_year = datetime.now().year
app.config['opcion'] = None
app.config['driver'] = None
app.config['api'] = None

def extract_username(url):
    parsed_url = urlparse(url)
    path_comp = parsed_url.path.split('/')
    if len(path_comp) > 2:
        return path_comp[2]
    else:
        return None

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
    app.config['api'] = Linkedin(usuario, contrasena)
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
    # - opcion de busqueda avanzada: ¿ubicacion?
    # - filtrado info de contacto (clasificado entre email corporativo o personal).
    opt = app.config['opcion']
    perfiles_visitados = []
    cuadro_texto = request.form.get('texto_busqueda')

    # Recupero la profundidad de la red (contactos de segundo grado, de tercer grado o todos los contactos)
    grado = request.form.get('grado')
    if grado == 'grade2':
        deep = '&network=%5B"S"%5D'
    elif grado == 'grade3':
        deep = '&network=%5B"O"%5D'
    else:
        deep = ''
    
    if opt == '1':
        # Uso el try-except para controlar el error que ocurriría si no se producen resultados en la búsqueda
        # (intentaría scrapear algo que no existe y se lanzaría la NoSuchElementException)
        try:
            contact_info = []
            # Averiguo cuántas páginas tengo que recorrer en total; para ello, me voy a la pagina 1
            app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")
            btn_pages = app.config['driver'].find_elements(By.XPATH, '//*[@class="artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view"]')
            botonera = [b for b in btn_pages]
            paginas = len(botonera) - 1
            # TODO: El error esta aqui abajo. ¿Por que?
            num_pags = botonera[paginas].get_attribute('data-test-pagination-page-btn')            
            print(f"****** Esto ha producido {num_pags} paginas de resultados")

            for pagina in range(int(num_pags)):

                # Primero me posiciono en la página de búsqueda y espero un poco
                app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}&page={pagina}")
                time.sleep(random.randint(1, 4))

                # Construyo la lista de perfiles a visitar
                profiles = app.config['driver'].find_elements(By.XPATH, '//*[@class="app-aware-link  scale-down "]')
                visit_profiles = [p for p in profiles]
                for p in visit_profiles:
                    # TODO: ¿Por qué en la primera página solo me visita 3 perfiles?
                    p_url = p.get_attribute('href')
                    app.config['driver'].execute_script(f"window.open('{p_url}');")
                    usuario = extract_username(p_url)
                    contact_info.append(app.config['api'].get_profile_contact_info(usuario))
                    time.sleep(random.randint(1, 4))
                
                # Ahora construyo la lista de nombres propios
                nombres_usuarios = app.config['driver'].find_elements(By.XPATH, '//span[@aria-hidden="true"]')
                names = [n.text for n in nombres_usuarios if len(n.text) > 0]
                for n in names:
                    perfiles_visitados.append(n)

                    # OJO: Si consiguiera ir a cada uno de los perfiles y extraer la nombre y puesto, se scrapearía así:
                    # - h1 class="text-heading-xlarge inline t-24 v-align-middle break-words" . text
                    # - div class="text-body-medium break-words" . text
                
            archivo = 'datos_contacto.csv'
            with open(archivo, mode='w', newline='') as f:
                writer = csv.writer(f)
                for row in contact_info:
                    writer.writerow(row)

        except NoSuchElementException:
            return ('Ha habido un error al visitar perfiles')
        finally:
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