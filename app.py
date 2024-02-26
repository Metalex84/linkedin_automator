from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)
driver = webdriver.Chrome()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/acciones', methods=['POST', 'GET'])
def acciones():
    opcion = request.form['opcion']
    return render_template('login.html', opcion=opcion)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Recupero la info del formulario
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
    time.sleep(3)

    return render_template('busqueda.html', usuario=usuario)


@app.route('/busqueda', methods=['POST', 'GET'])
def busqueda():
    texto = request.form.get('texto_busqueda')
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={texto}&origin=SWITCH_SEARCH_VERTICAL")
    time.sleep(2)
    # Aquí intento visitar todos los perfiles
    profiles_pattern = 'app-aware-link '
    profiles = driver.find_elements(By.XPATH, f'//*[@class="{profiles_pattern}"]')
    visit_profiles = [p for p in profiles]
    for p in visit_profiles:
    #driver.execute_script("arguments[0].click();", p)
        p_url = p.get_attribute('href')
        driver.execute_script(f"window.open('{p_url}');")
        print("Perfil visitado")
    driver.close()
    return "¡Hecho!"


if __name__ == '__main__':
    app.run(debug=True)