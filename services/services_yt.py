from repo.repo_yt import YtRepository

class SearchService:

    def __init__(self):
        self.repo = YtRepository()

    def buscar_playlist(self, url):
        resultado = self.repo.get_playlist(url)
        if not resultado:
            return
        return resultado
    
    def descargar_playlist(self, url):
        resultado = self.repo.descargar_playlist(url)
        if not resultado:
            raise Exception("No se pudo descargar la playlist")
        return resultado
    
    def buscar_canciones(self, query, cant):
        resultados = self.repo.buscar_en_yt(query, cant)
        return [r for r in resultados if r['duration']]

    def buscar_canciones_stream(self, query):
            resultados = self.repo.buscar_en_yt_stream(query)
            return [r for r in resultados if r['duration']]
    
    def descargar(self, urls):
        resultado = self.repo.descargar_de_yt(urls)
        if not resultado:
            return {
                "status": "error",
                "message": "No se pudo descargar"
            }

        return {
            "status": "ok",
            "message": f"Descarga completada: {len(resultado)} archivos descargados",
            "data": resultado
        }