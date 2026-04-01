from yt_dlp import YoutubeDL
import yt_dlp

class YtRepository:
    def descargar_dey_yt(self, urls):
        try: 
            opciones_descarga = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                    'no_progress':True,
                    'writethumbnail': True,  
                    'proxy': 'http://192.168.49.1:8282',
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
                    'outtmpl': '~/Música/%(title)s.%(ext)s',
                }
            resultados=[]
            
            with YoutubeDL(opciones_descarga) as ydl:
                for url in urls:
                    info = ydl.extract_info(url, download=True)

                    resultados.append({
                        'title': info.get('title'),
                        'path': ydl.prepare_filename(info)
                    })

            return resultados

        except yt_dlp.utils.DownloadError as e:
            print(f"Error de descarga o de conexion: {e}")
            return[]
    
    def buscar_en_yt(self, query, cant_opciones):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'no_progress': True,
                'proxy': 'http://192.168.49.1:8282'
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