from repo.repo_yt import YtRepository

class SearchService:

    def __init__(self):
        self.repo = YtRepository()

    def buscar_canciones(self, query, cant):
        resultados = self.repo.buscar_en_yt(query, cant)
        return [r for r in resultados if r['duration']]
    
    def descargar(self, urls):
        resultado = self.repo.descargar_dey_yt(urls)
        if not resultado:
            return {
                "status": "error",
                "message": "No se pudo descargar"
            }

        return {
            "status": "ok",
            "message": f"{len(resultado)} Descargados:",
            "data": resultado
        }