from sqlite.db_conexion import get_conexion
from sqlite.db_consultas import save_cola, get_canciones, get_playlists, delete_playlist, updateplaylist


def eliminar_playlist(id):
    if not id:
        return False
    try:
        with get_conexion() as con:
            cur=con.cursor()
            delete_playlist(id, cur)
            return True
    except Exception as e:
        raise e
    
def obtener_playlist():
    return get_playlists()

def obtener_canciones(id):
    return get_canciones(id)

def actualizar_playist(id, info):
    if not id or not info:
        return False
    try:
        with get_conexion() as con:
            cur = con.cursor()
            updateplaylist(cur, id, info)
            return True
    except Exception as e:
        raise e
        
def guardar_cola(name, info):
    if not name or not info:
        print("El nombre o la cola están vacíos.")
        return False
    try:
        with get_conexion() as con:
            cur = con.cursor()
            save_cola(cur, name, info)
            return True

    except Exception as e:
        print(f"Error al guardar la playlist: {e}")
        raise e