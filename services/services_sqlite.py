from sqlite.db_conexion import get_conexion
from sqlite.db_consultas import sqliteQueries

class sqliteService:
    def __init__(self):
        self.queries = sqliteQueries()
        
    def eliminar_playlist(self, id):
        if not id:
            return False
        try:
            with get_conexion() as con:
                cur=con.cursor()
                self.queries.delete_playlist(id, cur)
                return True
        except Exception as e:
            raise e
        
    def obtener_playlist(self):
        return self.queries.get_playlists()

    def obtener_canciones(self, id):
        return self.queries.get_canciones(id)

    def actualizar_playist(self, id, info):
        if not id or not info:
            return False
        try:
            with get_conexion() as con:
                cur = con.cursor()
                self.queries.updateplaylist(cur, id, info)
                return True
        except Exception as e:
            raise e
            
    def guardar_cola(self, name, info):
        if not name or not info:
            print("El nombre o la cola están vacíos.")
            return False
        try:
            with get_conexion() as con:
                cur = con.cursor()
                self.queries.save_cola(cur, name, info)
                return True

        except Exception as e:
            print(f"Error al guardar la playlist: {e}")
            raise e