from rich.panel import Panel
from rich.prompt import Prompt

from ui.ui_banner import baner


def main_playlist(console):
    while True:
        baner(console)
        console.print(Panel("""[bold bright_white]
        1.Ver 
        2.Crear
        0.Salir
                            """, 
                            style='#9999FF',
                            title='[black on #3999FF]Playlist'))
        s=Prompt.ask('Elije')

        if s=='0':
            break