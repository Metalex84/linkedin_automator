''' 
Copyright (c) 2024 [Alejandro Gonzalez Venegas]

Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
https://creativecommons.org/licenses/by-nc/4.0/
'''

import sqlite3 as sql


def insert_user(usuario, hash, connections_left, messages_left, visits_left):
    '''Inserta un usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO usuarios (usuario, password, connections_left, messages_left, visits_left) VALUES (?, ?, ?, ?, ?)""", 
        (usuario, hash, connections_left, messages_left, visits_left)
        )
    conn.commit()
    conn.close()



def get_user_by_name(usuario):
    '''Devuelve todos los datos de un usuario por su nombre'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT * FROM usuarios WHERE usuario = '{usuario}'"""
        )
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    users_info = []
    for u in users:
        users_info.append({
            'id': u[0],
            'usuario': u[1],
            'password': u[2],
            'connection': u[3],
            'connections_left': u[4],
            'messages_left': u[5],
            'visits_left': u[6]
        })
    return users_info



def get_user_by_id(id):
    '''Obtiene un usuario por su id; si no lo encuentra, no devuelve 'None' sino campos vacios'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT * FROM usuarios WHERE id = {id}"""
        )
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    if user:
        return {
            'id': user[0],
            'usuario': user[1],
            'password': user[2],
            'connection': user[3],
            'connections_left': user[4],
            'messages_left': user[5],
            'visits_left': user[6]
        }
    else:
        return {
            'id': 0,
            'usuario': '',
            'password': '',
            'connection': '',
            'connections_left': '',
            'messages_left': '',
            'visits_left': ''
        }


def set_password_by_id(password, id):
    '''Fija la contraseña por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE usuarios SET password = ? WHERE id = ?""", 
        (password, id)
        )
    conn.commit()
    conn.close()



def set_last_connection_by_id(last_connection, id):
    '''Fija la ultima fecha y hora de conexión por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute("""UPDATE usuarios SET last_connection = ? WHERE id = ?""",
                   (last_connection, id))
    last_connection = cursor.fetchone()
    conn.commit()
    conn.close()



def get_last_connection_by_id(id):
    '''Obtiene la última fecha y hora de conexión por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT last_connection FROM usuarios WHERE id = {id}"""
        )
    last_connection = cursor.fetchone()
    conn.commit()
    conn.close()
    if last_connection:
        return last_connection[0]
    else:
        return None



def set_connections_left_by_id(connections_left, id):
    '''Fija el número de conexiones restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE usuarios SET connections_left = ? WHERE id = ?""", 
        (connections_left, id)
        )
    conn.commit()
    conn.close()



def set_messages_left_by_id(messages_left, id):
    '''Fija el número de mensajes restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE usuarios SET messages_left = ? WHERE id = ?""", 
        (messages_left, id)
        )
    conn.commit()
    conn.close()



def set_visits_left_by_id(visits_left, id):
    '''Fija el número de visitas restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE usuarios SET visits_left = ? WHERE id = ?""", 
        (visits_left, id)
        )
    conn.commit()
    conn.close()



def get_messages_left_by_id(id):
    '''Obtiene el número de mensajes restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT messages_left FROM usuarios WHERE id = {id}"""
        )
    messages_left = cursor.fetchall()
    conn.commit()
    conn.close()
    if messages_left:
        return messages_left[0][0]
    else:
        return None



def get_connections_left_by_id(id):
    '''Obtiene el número de conexiones restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT connections_left FROM usuarios WHERE id = {id}"""
        )
    connections_left = cursor.fetchall()
    conn.commit()
    conn.close()
    if connections_left:
        return connections_left[0][0]
    else:
        return None
    


def get_visits_left_by_id(id):
    '''Obtiene el número de visitas restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT visits_left FROM usuarios WHERE id = {id}"""
        )
    visits_left = cursor.fetchall()
    conn.commit()
    conn.close()
    if visits_left:
        return visits_left[0][0]
    else:
        return None