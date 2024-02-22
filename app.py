from flask import Flask, render_template, request, redirect, url_for
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    user = request.form['usuario']
    passw = request.form['contraseña']
    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com')
    username = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    password = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    # user = 'agonzalez.venegas@outlook.com'
    # passw = 'ktmEXC-2022l'
    username.send_keys(user)
    password.send_keys(passw)
    submit = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submit.click()
    time.sleep(2)
    return render_template('bienvenida.html', driver=driver)

@app.route('/bienvenida', methods=['POST', 'GET'])
def bienvenida(driver):
    busqueda = request.form['busqueda']
    # busqueda = "Horeca"
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={busqueda}&origin=SWITCH_SEARCH_VERTICAL")
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