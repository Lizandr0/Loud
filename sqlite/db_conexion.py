import os
import sqlite3

def get_conexion():
    # Define la ruta dinámica en el directorio personal del usuario (XDG Standard)
    user_data_dir = os.path.expanduser("~/.local/share/loud")
    os.makedirs(user_data_dir, exist_ok=True)
    
    ruta_db = os.path.join(user_data_dir, "loud_db.db")
    return sqlite3.connect(ruta_db)