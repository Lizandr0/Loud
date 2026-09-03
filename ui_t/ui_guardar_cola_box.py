from textual.widgets import Input, Static, Footer, Button
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen

class SaveCola(ModalScreen):
    BINDINGS = [
        ("escape", "atras", "Atrás"),
        
    ]
    
    def compose(self) -> ComposeResult:
        with Vertical(id='save-cola-box'):
            yield Static("Guardar la cola como una Playlist!", id='title-save-cola')
            yield Input(placeholder="Nombre de la Playlist", id="name-cola")
            yield Button("GUARDAR", id="btn-save-cola")
        yield Footer()

    def action_atras(self):
        self.app.pop_screen()

    def on_mount(self):
        self.query_one("#name-cola", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id=="btn-save-cola":
            self._submit()
        else:
            self.dismiss(None)
            
    def _submit(self)->None:
        name_input = self.query_one("#name-cola", Input)
        name = name_input.value.strip()
        if name:
            self.dismiss(name)
        else:
            self.notify(
                "Escribe un nombre válido", title="Error", severity="error"
            )