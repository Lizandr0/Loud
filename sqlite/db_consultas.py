from sqlite.db_conexion import get_conexion

class sqliteQueries:
    def __init__(self):
        pass
    def save_cola(self, cursor, name, info):
        try:
            cursor.execute('''
    insert into playlists (nombre) values (?)
            ''', (name,))
            playlist_id=cursor.lastrowid

            songs_data =[(playlist_id, song["title"], song["duration"], song["url"]) for song in info]
            cursor.executemany('''
    insert into playlist_songs(playlist_id, titulo, duracion, url)
    values(?,?,?,?)
            ''', songs_data,)
        except Exception as e:
            raise e
        
    def updateplaylist(self, cursor, id, info):
        try:
            cursor.execute("DELETE from playlist_songs WHERE playlist_id=?", (id,))

            songs_data =[(id, song["title"], song["duration"], song["url"]) for song in info]
            cursor.executemany('''
            insert into playlist_songs(playlist_id, titulo, duracion, url)
            values(?,?,?,?)''', songs_data,)
        except Exception as e:
            raise e
        
    def delete_playlist(self, id, cur):
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute('DELETE FROM playlists WHERE id=?', (id,))

    def get_playlists(self):
        with get_conexion() as con:
            cur=con.cursor()
            cur.execute('select* from playlists')
            return cur.fetchall()

    def get_canciones(self, id):
        with get_conexion() as con:
            cur=con.cursor()
            cur.execute('select titulo, duracion, url from playlist_songs where playlist_id=?', (id,))

            info=cur.fetchall()

            return [
                    {"title": row[0], "duration": row[1], "url": row[2]}
                    for row in info
                ]
