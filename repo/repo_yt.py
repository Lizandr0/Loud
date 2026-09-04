from yt_dlp import YoutubeDL
import yt_dlp
import os
import subprocess

from config import COOKIES_PATH, YTDLP_BIN

class YtRepository:
    def get_playlist(self, url):
        try:
            opciones_descarga = {
                'quiet': True,
                'no_progress': True,
                'extract_flat': True,
                'skip_download': True,
                'ignoreerrors': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios']
                    }
                }
            }
            with YoutubeDL(opciones_descarga) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return []

                if 'entries' in info:
                    canciones = []
                    for e in info['entries']:
                        if e and e.get('id'):
                            duracion_sec = e.get('duration')
                            if duracion_sec is not None:
                                mins, secs = divmod(int(duracion_sec), 60)
                                duracion_str = f"{mins:02d}:{secs:02d}"
                            else:
                                duracion_str = "--:--"

                            canciones.append({
                                'title': e.get('title', 'Sin título'),
                                'url': f"https://www.youtube.com/watch?v={e.get('id')}",
                                'duration': duracion_str
                            })
                    return canciones
                else:
                    duracion_sec = info.get('duration')
                    if duracion_sec is not None:
                        mins, secs = divmod(int(duracion_sec), 60)
                        duracion_str = f"{mins:02d}:{secs:02d}"
                    else:
                        duracion_str = "--:--"

                    return [{
                        'title': info.get('title', 'Sin título'),
                        'url': f"https://www.youtube.com/watch?v={info.get('id')}",
                        'duration': duracion_str
                    }]

        except yt_dlp.utils.DownloadError as e:
            print(f"Error de descarga o de conexion: {e}")
            return []
            
    def descargar_playlist(self, url):
        try:
            try:
                ruta_base = subprocess.check_output(
                    ['xdg-user-dir', 'MUSIC'],
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                ruta_base = os.path.expanduser('~/Music')

            if not ruta_base:
                ruta_base = os.path.expanduser('~/Music') 

            os.makedirs(ruta_base, exist_ok=True)

            ruta_salida = os.path.join(ruta_base, '%(title)s.%(ext)s')
            opciones_descarga = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'no_progress': True,
                'writethumbnail': True,
                'outtmpl': ruta_salida
            }
            with YoutubeDL(opciones_descarga) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if 'entries' in info:
                    resultados = []
                    for e in info['entries']:
                        if e: 
                            if 'duration' not in e or e.get('duration') is None:
                                e['duration'] = 0
                            
                            resultados.append({
                                'title': e.get('title', 'Desconocido'),
                                'path': ydl.prepare_filename(e)
                            })
                    return resultados
                else:
                    if info:
                        if 'duration' not in info or info.get('duration') is None:
                            info['duration'] = 0
                        return [{
                            'title': info.get('title', 'Desconocido'),
                            'path': ydl.prepare_filename(info)
                        }]
                    return []
                    
        except yt_dlp.utils.DownloadError as e:
            print(f"Error de descarga o de conexion: {e}")
            return []  
    


    def descargar_de_yt(self, urls):
        try: 
            try:
                ruta_base = subprocess.check_output(
                    ['xdg-user-dir', 'MUSIC'],
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                ruta_base = os.path.expanduser('~/Music')

            if not ruta_base:
                ruta_base = os.path.expanduser('~/Music') 

            os.makedirs(ruta_base, exist_ok=True)
            
            ruta_salida = os.path.join(ruta_base, '%(title)s.%(ext)s')
            opciones_descarga = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'no_progress': True,
                'writethumbnail': True,
                'cookiefile': COOKIES_PATH,
                'ignoreerrors': False, 
                'socket_timeout': 15,
                'retries': 3,
                'noplaylist': True,

                
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'EmbedThumbnail',
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }
                ],
                'outtmpl': ruta_salida,
            }

            resultados = []

            if isinstance(urls, str):
                urls = [urls]

            with yt_dlp.YoutubeDL(opciones_descarga) as ydl:
                for url in urls:
                    info = ydl.extract_info(url, download=True)
                    
                    if info:
                        filename = ydl.prepare_filename(info)
                        path_mp3 = os.path.splitext(filename)[0] + ".mp3"

                        resultados.append({
                            'title': info.get('title', 'Desconocido'),
                            'path': path_mp3
                        })

            return resultados

        except yt_dlp.utils.DownloadError as e:
            print(f"Error de descarga o de conexion: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado en la descarga: {e}")
            return []
    
    def buscar_en_yt(self, query, cant_opciones):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'no_progress': True
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f'ytsearch{cant_opciones}:{query}',
                    download=False
                )

            resultados = []

            for e in info['entries']:
                resultados.append({
                    'title': e.get('title'),
                    'url': f"https://www.youtube.com/watch?v={e.get('id')}",
                    'duration': e.get('duration'),
                })

            return resultados

        except yt_dlp.utils.DownloadError as e:
            print(f"ERROR DE BUSQUEDA: {e}")
            return []

        except OSError as e:
            print(f"Error de conexion: {e}")
            return []
        
    def buscar_en_yt_stream(self, query):
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'no_progress': True
                }
    
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(
                        f'ytsearch{5}:{query}',
                        download=False
                    )
    
                resultados = []
    
                for e in info['entries']:
                    resultados.append({
                        'title': e.get('title'),
                        'url': f"https://www.youtube.com/watch?v={e.get('id')}",
                        'duration': e.get('duration'),
                    })
    
                return resultados
    
            except yt_dlp.utils.DownloadError as e:
                print(f"ERROR DE BUSQUEDA: {e}")
                return []
    
            except OSError as e:
                print(f"Error de conexion: {e}")
                return []