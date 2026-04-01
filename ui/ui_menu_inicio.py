from rich.panel import Panel
from rich.prompt import Prompt
import sys
from ui.ui_banner import baner
from ui.ui_descargaryt import main_descargar
from ui.ui_menu_player import main_rep

def main_menu(console):
    while True:
        baner(console)
        console.print(Panel('''[bold #E5E5FF]
                1.Descargar de [bold white on red]YouTube[/]
                2.Reproducir [bold black on yellow]ARCHIVOS LOCALES[/].mp3
                0.SALIR
                                ''', 
                            title='[bold #CCCCFF]Solo buena musica cabrones!',
                            border_style='#9999FF'))
        s=Prompt.ask('Elije')
        
        if s=='0':
            a=Prompt.ask("[bold bright_red]Deseas salir bro? [yellow](Y/N)")
            if a.lower() == 'y':
                console.print(f'''[#9999FF]
    GRACIAS POR USAR MI SOFTWARE :)
    PYTHON: {sys.version}
    EJECUTADO EN: {sys.platform}
                            ''')
                break
            else:
                return main_menu(console)
            
        elif s=='1':
            main_descargar(console)
        elif s=='2':
            main_rep(console)
        else:
            console.print('Jodete bro, solo hay tres opciones', style='black on red')
            input('->')