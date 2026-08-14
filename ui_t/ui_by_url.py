from textual.widgets import Input, Static, Header, Footer, Button
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen

from services.services_yt import SearchService

class ByUrl(ModalScreen):
    theme='tokyo-night'
    BINDINGS = [
        ('ctrl+x', 'limpiar', 'Limpiar todo'),
        ("escape", "atras", "Atrás"),
        
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='search-tab-url'):
            yield Static("Descarga con una url de [white on red]YouTube[/]", id='title-by-url')
            yield Input(placeholder="Pega aqui tu URL", id="by_url_input")
            yield Button("Descargar", id="by_url_download_button")
        yield Footer()

    def on_mount(self):
        self.query_one("#by_url_input").focus()
        self.notify("Descarga una canción desde una URL", title="LOUD",severity="info")

    def action_atras(self):
        self.app.pop_screen()

    def action_limpiar(self):
        self.query_one("#by_url_input").value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "by_url_download_button":
            url = self.query_one("#by_url_input").value
            if url:
                service = SearchService()
                try:
                    service.descargar([url])
                    self.notify(f"Descarga completada para {url}", severity="success", title='LOUD')
                    self.action_limpiar()
                except Exception as e:
                    self.notify(f"Error al descargar: {str(e)}", severity="error", title="LOUD")
                    self.action_limpiar()
            else:
                self.notify("Por favor, ingresa una URL válida.", severity="warning", title="LOUD")
                self.action_limpiar()