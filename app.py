from flask import Flask, render_template, request, url_for, redirect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time

app = Flask(__name__)
current_year = datetime.now().year
app.config['opcion'] = None
driver = webdriver.Chrome()


@app.route('/')
def index():
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
    driver.get('https://www.linkedin.com')
    # Busco los campos de usuario y contraseña para meter los mios
    username = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    password = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    username.send_keys(usuario)
    password.send_keys(contrasena)
    # Busco el boton de submit para enviar el formulario web
    submit = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submit.click()
    time.sleep(1) # Ojo, numero aleatorio !!! 
    return render_template('busqueda.html', usuario=usuario, current_year=current_year)


@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():

    texto = request.form.get('texto_busqueda')
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={texto}&origin=SWITCH_SEARCH_VERTICAL")
    time.sleep(1) # Ojo, numero aleatorio !!! 
    # OJO: empezar con la paginación! Averiguar cuántas páginas de resultados se producen 
    # OJO: implementar opcion de busqueda avanzada: contactos de 2 o 3 grado, ubicacion, 
    opt = app.config['opcion']
    if opt == '1':
        profiles_pattern = 'app-aware-link '
        profiles = driver.find_elements(By.XPATH, f'//*[@class="{profiles_pattern}"]') # and @tabindex="-1"]')
        visit_profiles = [p for p in profiles]
        # OJO: copiar el contenido de visit_profiles a una lista nueva para que no se pierda al cerrar el navegador
        for p in visit_profiles:
            p_url = p.get_attribute('href')
            driver.execute_script(f"window.open('{p_url}');")
            # En cada iteracion se abre una nueva pestaña con el perfil de la persona pero con webdriver, no con JS
            # Utiliza otro webdriver: driver2.get(p_url)
            # OJO: implementar un tiempo aleatorio para que no se bloquee el navegador
            # driver.close()
    
    elif opt == '2':
        print('Escribir mensajes no implementado aun')
        
    elif opt == '3':
        print('Enviar invitaciones no implementado aun')
        # Para conectar seria: driver.execute_script("arguments[0].click();", p)

    else:
        return render_template('index.html', current_year=current_year)

    driver.close()
    return render_template("done.html", profiles=visit_profiles, current_year=current_year)

    # Filtrado info de contacto (clasificado entre email corporativo o personal).


if __name__ == '__main__':
    app.run(debug=True)