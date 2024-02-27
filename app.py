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
    time.sleep(1)
    return render_template('busqueda.html', usuario=usuario, current_year=current_year)


@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():

    texto = request.form.get('texto_busqueda')
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={texto}&origin=SWITCH_SEARCH_VERTICAL")
    time.sleep(1)

    opt = app.config['opcion']
    if opt == '1':
        profiles_pattern = 'app-aware-link '
        profiles = driver.find_elements(By.XPATH, f'//*[@class="{profiles_pattern}"]')
        visit_profiles = [p for p in profiles]
        for p in visit_profiles:
            # Para conectar seria: driver.execute_script("arguments[0].click();", p)
            p_url = p.get_attribute('href')
            driver.execute_script(f"window.open('{p_url}');")
    
    elif opt == '2':
        print('Escribir mensajes no implementado aun')
        
    elif opt == '3':
        print('Enviar invitaciones no implementado aun')
    
    else:
        return render_template('index.html', current_year=current_year)

    driver.close()
    return render_template("done.html", profiles=visit_profiles, current_year=current_year)


if __name__ == '__main__':
    app.run(debug=True)