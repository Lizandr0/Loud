from repo.repo_spotify import Spotify

class SearchSpotify:
    def __init__(self):
        self.repo_spotify=Spotify()

    def buscar_canciones_spotify(self, url):
        canciones=self.repo_spotify.obtener_canciones_spotify_web(url)
        if not canciones:
            return
        return canciones