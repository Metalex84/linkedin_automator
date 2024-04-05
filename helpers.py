from flask import redirect, render_template, session
from functools import wraps
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By

import random
import time
import math


class Persona:
    ''' Clase que representa a una persona con su nombre y lo que tenga puesto como informacion principal de perfil'''
    def __init__(self, nombre, rol):
        self.nombre = nombre
        self.rol = rol



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



def apology(message, code=400):
    ''' Un renderizador de mensajes de error '''

    def escape(s):
        '''
        https://github.com/jacebrowning/memegen#special-characters
        '''
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code



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
