from textual.widgets import Input, Static, Header, Footer, Button, DataTable
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen

from services.services_yt import SearchService
from textual import work
class PlayList(ModalScreen):
    BINDINGS = [
        ("escape", "atras", "Atrás"),
        ('ctrl+x', 'limpiar', 'Limpiar todo'),
        ('d', 'descargar', 'Descargar selección'),
        ('ctrl+g', 'save_playlist', 'Guardar como Playlist'),
    ]

    def __init__(self):
        super().__init__()
        self.playlist_lista=[]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='playlist-container'):
            yield Static("Buscar playlist de [white on red]YouTube[/]", id="playlist_title")
            with Horizontal(id='search-tab'):
                yield Input(placeholder="Pega aqui tu URL", id="url_input")
                yield Button("Buscar", id="search_button")
            with Vertical(id='playlist-tab-container'):
                yield DataTable(id="playlist_table")
                yield Button('Descargar todo', id='download_button')
        yield Footer()

    def action_atras(self):
        self.app.pop_screen()

    def action_limpiar(self):
        self.query_one("#url_input", Input).value = ""
        self.query_one("#playlist_table", DataTable).clear()
        
    def actualizar_tabla(self, info):
        tabla=self.query_one("#playlist_table", DataTable)
        tabla.clear()
        if not info:
            self.notify("No se encontraron videos en la playlist.", title="Información")
            return
        for video in info:
            tabla.add_row(video['title'], str(video['duration']), str(video['url']))

    @work
    async def action_save_playlist(self)->None:
        songs=self.playlist_lista
        self.app.queue.clear()
        for song in songs:
            self.app.queue.append(song)
        player=self.app.query_one("#nav_player_")

        player.action_save_cola()
        self.playlist_lista.clear()

    def action_descargar(self) -> None:
        tabla = self.query_one("#playlist_table", DataTable)

        if tabla.cursor_row is not None:
            try:
                coordenadas = tabla.cursor_coordinate
                row_key, _ = tabla.coordinate_to_cell_key(coordenadas)
                fila = tabla.get_row(row_key)
                url = str(fila[2]).strip()
                
                self.notify(f"Iniciando descarga: {url}")

                self.run_worker(
                    lambda: self.hilo_descarga(url),
                    exclusive=True,
                    thread=True   
                )
            except Exception as e:
                self.notify(f"Error al capturar la fila: {e}", severity="error")
    def limpiar_campo(self):
        self.query_one("#url_input", Input).value = ""

    def hilo_descarga(self, url: str) -> None:
        try:
            descarga = SearchService().descargar([url])
            
            if descarga.get("status") == "ok":
                mensaje_exito = descarga.get("message", "¡Descarga completada!")
                self.notify(mensaje_exito)
            else:
                mensaje_error = descarga.get("message", "Error desconocido")
                self.notify(f"Error: {mensaje_error}", severity="error")
                
        except Exception as e:
            self.notify(f"Error crítico en el hilo: {e}", severity="error")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search_button":
            self.notify("Buscando canciones en la playlist...")

            url = self.query_one("#url_input", Input).value
            if not url:
                self.notify("Por favor, ingresa una URL válida.", title="Error")
                self.limpiar_campo()
                return
            try:
                self.playlist_lista = self.buscar_playlist(url)
                self.actualizar_tabla(self.playlist_lista)

            except Exception as e:
                self.actualizar_tabla([{
                    'title': 'No se encontraron videos', 
                    'duration': '', 
                    'url': ''
                }])
                self.notify(f"Error: {str(e)}", title="Error")
                self.limpiar_campo()

        elif event.button.id == "download_button":
            url=self.query_one("#url_input", Input).value
            if not url:
                self.notify("Por favor, ingresa una URL válida.", title="Error")
                self.limpiar_campo()
                return
            self.notify("Iniciando descarga de la playlist...", title="Descarga")
            self.limpiar_campo()
            try:
                service = SearchService()
                if service.descargar_playlist(url):
                    self.notify(f"Descargaste {len(service.buscar_playlist(url))} canciones!", title="Éxito")
            except Exception as e:
                self.notify(f"Error al descargar la playlist: {str(e)}", title="Error")
                self.limpiar_campo()

    def on_mount(self) -> None:
        self.query_one("#playlist_table", DataTable).add_columns("Título", "Duración", "URL")
        self.query_one("#playlist_table", DataTable).cursor_type = "row"
        self.query_one("#playlist_table", DataTable).show_cursor = True
        self.query_one("#playlist_table", DataTable).zebra_stripes = True

    def buscar_playlist(self, url):
        service = SearchService()
        return service.buscar_playlist(url)