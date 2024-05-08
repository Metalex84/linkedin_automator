from flask import redirect, render_template, session
from functools import wraps
from urllib.parse import urlparse

import random
import time
import math


MAX_RESULT_PAGES = 100

MAX_MONTHLY_VISITS = 100
MAX_DAILY_MESSAGES = 100
MAX_WEEKLY_CONNECTIONS = 100

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ERR_NO_USERNAME = "¡Introduce tu nombre de usuario!"
ERR_NO_PASSWORD = "¡Introduce tu contraseña!"
ERR_NO_NEW_PASSWORD = "¡Introduce tu nueva contraseña!"
ERR_NO_CONFIRM_PASSWORD = "¡Confirma tu nueva contraseña!"
ERR_USER_OR_PASS_WRONG = "¡Usuario o contraseña incorrectos!"
ERR_USER_ALREADY_EXISTS = "¡Este nombre de usuario ya existe!"
ERR_CONFIRM_PASSWORD = "¡Confirma tu contraseña!"
ERR_PASSWORDS_NOT_MATCH = "¡Las contraseñas no coinciden!"
ERR_CORPORATE_EMAIL = "¡Utiliza tu correo corporativo como nombre de usuario!"
ERR_EMPTY_MESSAGE = "¡Introduce un mensaje!"
ERR_NO_LINKEDIN_USER = "¡Introduce un nombre de usuario de LinkedIn!"
ERR_NO_LINKEDIN_PASS = "¡Introduce una contraseña de LinkedIn!"
ERR_LINKEDIN_LOGIN_WRONG = "¡Usuario o contraseña de LinkedIn incorrectos!"
ERR_NO_SHOTS_LEFT = "¡No tienes suficientes acciones restantes!"
ERR_NUMERICAL_SHOTS = "Por favor, introduce un número entre 1 y "
ERR_RANGE_INT = "¡Introduce un entero positivo!"

ACTION_VISIT_PROFILES = "visitar perfiles"
ACTION_WRITE_MESSAGES = "escribir mensajes"
ACTION_SEND_CONNECTIONS = "enviar invitaciones"

ACTION_PROFILE_VISITED = 'Perfil visitado'
ACTION_MESSAGE_WRITTEN = 'Mensaje enviado'
ACTION_CONNECTION_SENT = 'Solicitud de conexión'

URL_LINKEDIN_HOME = "https://www.linkedin.com"
URL_LINKEDIN_LOGIN = "https://www.linkedin.com/uas/login-submit"
URL_LINKEDIN_SEARCH_PEOPLE = "https://www.linkedin.com/search/results/people/?keywords="

ELEMENT_SESSION_KEY = "//*[@id='session_key']"
ELEMENT_SESSION_PASSWORD = "//*[@id='session_password']"
ELEMENT_BUTTON_SUBMIT = "//button[@type='submit']"
ELEMENT_EMPTY_STATE = '//h2[contains(@class, "artdeco-empty-state__headline")]'
ELEMENT_PAGE_PROFILES = '//*[@class="app-aware-link  scale-down "]'
ELEMENT_BUTTON_CONNECT = "Conectar"
ELEMENT_BUTTON_SEND_NOW = "//button[@aria-label='Enviar ahora']"

DEEP_2_3 = '&network=%5B"S"%2C"O"%5D'
DEEP_1 = '&network=%5B"F"%5D'
DEEP_2 = '&network=%5B"S"%5D'

PATH_WELCOME_NAME = "/html/body/div[6]/div[3]/div/div/div[2]/div/div/div/div/div[1]/div[1]/a/div[2]"
PATH_NUMBER_RESULTS = "//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2"

OUTPUT_CSV = "perfiles.csv"

def path_name(i):
    return f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[1]/div/span[1]/span/a/span/span[1]"

def path_role(i):
    return f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[2]"
                        



class Persona:
    ''' Clase que representa a una persona con su nombre y lo que tenga puesto como informacion principal de perfil'''
    def __init__(self, nombre, rol, url):
        self.nombre = nombre
        self.rol = rol
        self.url = url
        


def extract_username(url):
    ''' Funcion que manipula la url para extraer el nombre de usuario de LinkedIn '''
    parsed_url = urlparse(url)
    path_comp = parsed_url.path.split('/')
    if len(path_comp) > 2:
        return path_comp[2]
    else:
        return None



def wait_random_time():
    ''' Funcion que fuerza un tiempo de espera aleatorio entre 1 y 7 segundos para simular comportamiento humano '''
    time.sleep(random.randint(1, 7))



def parse_time(seconds):
    ''' Funcion que convierte el tiempo en segundos a un formato de horas, minutos y segundos'''
    horas = int (seconds // 3600)
    minutos = int ((seconds % 3600) // 60)
    segundos = int (seconds % 60)
    resultado = f"{horas} horas, {minutos} minutos y {segundos} segundos"
    return resultado



def number_of_pages(str_results):
    ''' Funcion que devuelve el numero de paginas de resultados de busqueda en funcion del numero de resultados que se han producido '''
    num_results = str_results.text.split(' ')
    try:
        ''' Si el número de resultados es mayor a 999, el texto se divide en dos partes '''
        resultados = int(num_results[0])
    except ValueError:
        buffer = num_results[1].split('.')
        resultados = int(buffer[0].join(buffer[1]))
    finally:
        return (math.ceil(resultados / 10))



def check_valid_username(username):
    ''' Funcion que comprueba si el nombre de usuario se ajusta al email corporativo '''
    str = username.split('@')
    if len(str) != 2:
        return False
    if str[1] == 'horecarentable.com':
        return True
    else:
        return False
    
    

def check_number(number, maximum):
    ''' Funcion que comprueba si el numero de shots maximo que el usuario introduce está en el rango correcto y no son caracteres no numéricos'''
    try:
        shots = int(number)
        if shots <= 0:
            return False
        elif shots > int(maximum):
            return False
        else:
            return shots
    except ValueError:
        return False
    


def login_required(f):
    '''
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
