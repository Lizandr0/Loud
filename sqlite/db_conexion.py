import os
import sqlite3
user_data_dir = os.path.expanduser("~/.local/share/loud")
os.makedirs(user_data_dir, exist_ok=True)

def inicializar_db():
    os.makedirs(user_data_dir, exist_ok=True)
    conexion = sqlite3.connect(os.path.join(user_data_dir, "loud_db.db"))
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            titulo TEXT NOT NULL,
            duracion TEXT,
            url TEXT NOT NULL,
            FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()
    conexion.close()

def get_conexion():
    inicializar_db()
    ruta_db = os.path.join(user_data_dir, "loud_db.db")
    return sqlite3.connect(ruta_db)