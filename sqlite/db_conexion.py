import sqlite3

import os

def get_conexion():
    ruta_db=os.path.join('../loud/sqlite', 'loud_db.db')
    return sqlite3.connect(ruta_db)
