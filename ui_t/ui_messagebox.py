from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Input, Button
from textual.screen import ModalScreen

class Msg(ModalScreen[bool]):
    def __init__(self, mesaje:str):
        super().__init__()
        self.mensaje=mesaje
    BINDINGS=[
        ('escape', 'atras', 'atras'),
    ]
    def compose(self):
        yield Vertical(
            Static(self.mensaje, id='mensaje-valid'),
            Button('SI', id='ok'),
            Button('NO', id='not'),
            id='msgBox'
        )

    def on_button_pressed(self, event:Button.Pressed)->None:
        if event.button.id=='ok':
            self.dismiss(True)
        if event.button.id=='not':
            self.dismiss(False)

    def action_atras(self)->None:
        self.dismiss(False)