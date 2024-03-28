from flask import Flask, render_template, request, url_for, redirect
from flask_session import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from werkzeug.security import generate_password_hash, check_password_hash
from linkedin_api import Linkedin
from urllib.parse import urlparse
from datetime import datetime
import random
import time
import math
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
    

    # TODO: A profundidad 1 -> escribir mensajes a contactos. (NO COMBINAR PROFUNDIDADES)
    # TODO: A profundidad 2 -> enviar invitaciones a contactos y visita de perfiles
    # TODO: A profundidad 3 -> visitar perfiles
    # TODO: tratar de recopilar nombre y cargo de cada perfil antes de visitarlo. 
    #       Si no se puede, quedarme con nombre extraido de url y utilizar linkedin_api para obtener los datos.
    # TODO: Implementar un área privada para que cada usuario pueda guardar sus preferencias (Registro y Login)
    # TODO: control error login LinkedIn
    # TODO: control error busqueda LinkedIn (la busqueda no produjo resultados)
    # TODO: perguntar seleccionar al usuario cuántas acciones quiere hacer hoy (maximo de 120 por seguridad)
    # TODO: implementar un contador regresivo para que, tras las acciones realizadas, el usuario vea cuántas le quedan durante el día.
    # TODO: implementar un reloj que cuente el tiempo de scrapeo y lo muestre al finalizar
    # TODO: implementar un último botón que permita al usuario descargar un archivo con el reporte de las acciones realizadas (y datos de contacto si se han recopilado)
    # TODO: en esto ultimo, si o si los datos de contacto en un CSV en una estructura legible para Pabbly -> HubSpot


@app.route('/')
def index():
    return render_template('index.html', current_year=current_year)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return render_template('actions.html', current_year=current_year, username=request.form.get('username'))
    else:
        return redirect(url_for('index'))


@app.route('/acciones', methods=['POST', 'GET'])
def acciones():
    if request.method == 'POST':
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
        return redirect(url_for('index'))


@app.route('/linklogin', methods=['POST', 'GET'])
def linklogin():
    if request.method == 'POST':
        app.config['driver'] = webdriver.Chrome()
        app.config['driver'].maximize_window() # Prueba, a ver si esto es necesario o no.
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
    else:
        return redirect(url_for('index'))


@app.route('/busqueda', methods=['POST', 'GET'])
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
            try:
                start = time.time()
                contact_info = []
                app.config['driver'].get(f"https://www.linkedin.com/search/results/people/?keywords={cuadro_texto}{deep}")
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
                # Esto lo tendremos que modificar para limitar el número de perfiles visitados por día.
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
            except NoSuchElementException:
                return('No se han encontrado resultados')
            finally:
                return render_template("done.html", profiles=perfiles_visitados, current_year=current_year, tiempo=round(end - start, 2))

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
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()


    '''
    Al final habrá que hacer un área privada con preferencias de cada cual, con mapeo de las visitas (quién está conectado), y que se guarden
    las preferencias de cada usuario (credenciales de Linkedin, preferencias de busqueda, rol en la empresa, fotos, etcétera).
    '''