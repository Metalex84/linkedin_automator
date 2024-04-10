import sqlite3 as sql


def insert_user(usuario, hash, shots):
    '''Inserta un usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO usuarios (usuario, password, shots) VALUES (?, ?, ?)""", 
        (usuario, hash, shots)
        )
    conn.commit()
    conn.close()



def get_user_by_name(usuario):
    '''Obtiene un usuario por su nombre'''
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
            'shots': u[4]
        })
    return users_info



def get_user_by_id(id):
    '''Obtiene un usuario por su id'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT * FROM usuarios WHERE id = {id}"""
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
            'shots': u[4]
        })
    return users_info



def set_connection_by_id(connection, id):
    '''Fija la ultima fecha y hora de conexión por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute("""UPDATE usuarios SET connection = ? WHERE id = ?""",
                   (connection, id))
    last_connection = cursor.fetchone()
    conn.commit()
    conn.close()
    return last_connection



def get_connection_by_id(id):
    '''Obtiene la última fecha y hora de conexión por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT connection FROM usuarios WHERE id = {id}"""
        )
    connection = cursor.fetchall()
    conn.commit()
    conn.close()
    if connection:
        return connection[0][0]
    else:
        return None



def set_shots_by_id(shots, id):
    '''Fija el número de shots restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE usuarios SET shots = ? WHERE id = ?""", 
        (shots, id)
        )
    conn.commit()
    conn.close()



def get_shots_by_id(id):
    '''Obtiene el número de shots restantes por el id de usuario'''
    conn = sql.connect('linkedin.db')
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT shots FROM usuarios WHERE id = {id}"""
        )
    shots = cursor.fetchall()
    conn.commit()
    conn.close()
    if shots:
        return shots[0][0]
    else:
        return None