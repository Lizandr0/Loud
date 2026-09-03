from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import requests
import yt_dlp


class Spotify:
    def limpiar_texto(self, texto: str) -> str:
        if not texto:
            return ""
        return re.sub(r"\s+", " ", texto).strip()

    def _obtener_token_anonimo_spotify(self) -> str:
        try:
            res = requests.get(
                "https://open.spotify.com/get_access_token?reason=transport&productType=web_player",
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    )
                },
                timeout=5,
            )
            if res.status_code == 200:
                return res.json().get("accessToken", "")
        except Exception as e:
            print(f"[LOUD] Error obteniendo token de Spotify: {e}")
        return ""

    def _buscar_en_youtube(self, track: dict) -> dict | None:
        titulo = track.get("title", "").strip()
        artista = track.get("subtitle", "").strip()

        if not titulo:
            return None

        titulo_limpio = self.limpiar_texto(titulo)
        artista_limpio = self.limpiar_texto(artista)

        nombre_completo = (
            f"{titulo_limpio} - {artista_limpio}"
            if artista_limpio
            else titulo_limpio
        )

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "extract_flat": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"ytsearch1:{nombre_completo}", download=False
                )
                if info and "entries" in info and len(info["entries"]) > 0:
                    entry = info["entries"][0]
                    video_id = entry.get("id")

                    if video_id:
                        return {
                            "title": nombre_completo,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "duration": "spotify",
                            "source": "spotify",
                        }
        except Exception:
            pass

        return None

    def obtener_canciones_spotify_web(self, playlist_url: str) -> list[dict]:
        match_id = re.search(r"playlist/([a-zA-Z0-9]{22})", playlist_url)
        if not match_id:
            print("[LOUD] URL de Spotify no válida")
            return []

        playlist_id = match_id.group(1)

        token = self._obtener_token_anonimo_spotify()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        track_list_raw = []
        offset = 0
        limit = 100

        while True:
            api_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}"
            try:
                res = requests.get(api_url, headers=headers, timeout=10)

                if res.status_code != 200:
                    print(
                        f"[LOUD] API de Spotify devolvió HTTP {res.status_code},"
                        " intentando fallback..."
                    )
                    break

                data = res.json()
                items = data.get("items", [])
                if not items:
                    break

                for item in items:
                    track = item.get("track")
                    if track and track.get("name"):
                        titulo = track.get("name", "")
                        artistas = ", ".join([
                            a.get("name", "")
                            for a in track.get("artists", [])
                        ])
                        track_list_raw.append({
                            "title": titulo,
                            "subtitle": artistas,
                        })

                if data.get("next"):
                    offset += limit
                else:
                    break

            except Exception as e:
                print(f"[LOUD] Error en petición a Spotify API: {e}")
                break

        if not track_list_raw:
            try:
                embed_url = (
                    f"https://open.spotify.com/embed/playlist/{playlist_id}"
                )
                response = requests.get(embed_url, headers=headers, timeout=10)
                match_json = re.search(
                    r'<script id="__NEXT_DATA__"'
                    r' type="application/json">(.*?)</script>',
                    response.text,
                )
                if match_json:
                    data = json.loads(match_json.group(1))
                    entity = (
                        data.get("props", {})
                        .get("pageProps", {})
                        .get("state", {})
                        .get("data", {})
                        .get("entity", {})
                    )
                    track_list_raw = entity.get("trackList", [])
            except Exception as e:
                print(f"[LOUD] Fallback falló: {e}")

        if not track_list_raw:
            print("[LOUD] No se pudieron extraer canciones de la playlist.")
            return []

        print(
            f"[LOUD] Se extrajeron {len(track_list_raw)} canciones de Spotify."
            " Resolviendo enlaces en YouTube en paralelo..."
        )

        canciones = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self._buscar_en_youtube, track)
                for track in track_list_raw
            ]
            for future in as_completed(futures):
                resultado = future.result()
                if resultado:
                    canciones.append(resultado)

        return canciones