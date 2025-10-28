''' 
Copyright (c) 2024 [Alejandro Gonzalez Venegas]

Esta obra está bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
https://creativecommons.org/licenses/by-nc/4.0/
'''

import sqlite3
import os

def init_database():
    """
    Inicializa la base de datos si no existe.
    Crea la tabla 'usuarios' con la estructura necesaria.
    """
    db_path = 'linkedin.db'
    
    # Verificar si la base de datos ya existe
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        print(f"✓ La base de datos '{db_path}' ya existe.")
        return
    
    print(f"Creando base de datos '{db_path}'...")
    
    # Crear conexión y cursor
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            last_connection TEXT,
            connections_left INTEGER DEFAULT 0,
            messages_left INTEGER DEFAULT 0,
            visits_left INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✓ Base de datos creada exitosamente.")
    print(f"✓ Tabla 'usuarios' inicializada.")

if __name__ == '__main__':
    init_database()
