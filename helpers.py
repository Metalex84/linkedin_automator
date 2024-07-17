''' 
Copyright (c) 2024 [Alejandro Gonzalez Venegas]

Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
https://creativecommons.org/licenses/by-nc/4.0/
'''

from flask import redirect, session
from functools import wraps
from urllib.parse import urlparse

from random import randint
from time import sleep
from math import ceil



def path_name(i):
    return f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/div/div[1]/div/span[1]/span/a/span/span[1]"



def path_role(i): 
    return f"//div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div/div[2]/p"
                        


class Persona:
    ''' Clase que representa a una persona con su nombre y lo que tenga puesto como informacion principal de perfil'''
    def __init__(self, nombre, rol, url, public_url, mensaje):
        self._nombre = nombre
        self._rol = rol
        self._url = url
        self._public_url = public_url
        self._mensaje = mensaje
    
    def get_nombre(self):
        return self._nombre
    
    def set_nombre(self, nombre):
        self._nombre = nombre
    
    def get_rol(self):
        return self._rol
    
    def set_rol(self, rol):
        self._rol = rol
    
    def get_url(self):
        return self._url
    
    def set_url(self, url):
        self._url = url
    
    def get_public_url(self):
        return self._public_url

    def set_public_url(self, public_url):
        self._public_url = public_url    
    
    def get_mensaje(self):
        return self._mensaje

    def set_mensaje(self, mensaje):
        self._mensaje = mensaje
        



def extract_username(url):
    ''' Funcion que manipula la url para extraer el nombre de usuario de LinkedIn '''
    parsed_url = urlparse(url)
    path_comp = parsed_url.path.split('/')
    if len(path_comp) > 2:
        return path_comp[2]
    else:
        return None



def build_public_url(username):
    ''' Funcion que construye la url publica de LinkedIn a partir del nombre de usuario '''
    return f"https://www.linkedin.com/in/{username}"



def wait_random_time():
    ''' Funcion que fuerza un tiempo de espera aleatorio entre 1 y 7 segundos para simular comportamiento humano '''
    sleep(randint(1, 7))



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
        return (ceil(resultados / 10))



def check_valid_username(username):
    ''' Funcion que comprueba si el nombre de usuario se ajusta al formato email '''
    str = username.split('@')
    if len(str) != 2:
        return False
    else:
        return True
    # if str[1] == 'horecarentable.com':
    #    return True
    # else:
    #    return False

    

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
