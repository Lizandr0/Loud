from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from ui.ui_banner import baner
from ui.ui_playlist import main_playlist

import os
import time
from services.services_player import PlayerService
from repo.repo_audio import AudioRepository

def mostrar_musica(musica):
    tabla=Table(style='#3999FF')
    tabla.add_column('No.', style='bold bright_yellow')
    tabla.add_column('Cancion', style='bold bright_white')

    for i, cancion in enumerate(musica):
        tabla.add_row(f'{str(i)}', cancion)
    return tabla

def run_player(console):
    repo = AudioRepository()
    service = PlayerService()
    
    songs = repo.list_mp3s()
    tabla=mostrar_musica(songs)
    
    console.print(Panel(tabla, title='[black on #9999FF]Canciones en la carpeta', style='#9999FF'))
    try:
        choice = int(input("\nSelecciona el número de canción: "))
        song_path = repo.get_file_path(songs[choice])
        
        if service.play(song_path):
            console.print(Panel (f"""
                          
        [bold bright_white] {songs[choice]}

        """, title='[black on #9999FF]▶ Reproduciendo:',
        style='#9993FF'))
            
            console.print(Panel('[bold bright_white]|P|Pause/Play  |  |S|Stop/Salir', 
                                title='[black on #9999FF] Controles',
                                style='#9993FF'), justify='center')
            
            while True:
                status = service.get_status()
                print(f"\r⏱ {status['current']}s / {status['total']}s", end="", flush=True)
                
                # Esto es un input simple; para algo pro sin Enter 
                # podrías usar la librería 'readchar'
                cmd = input(" ").lower()
                
                if cmd == 'p':
                    service.toggle_pause()
                elif cmd == 's':
                    service.stop()
                    console.print("[bright_white on red]\nReproducción detenida.")
                    break
                
                time.sleep(0.5)
    except (ValueError, IndexError):
        console.print("Selección inválida.")
    except KeyboardInterrupt:
        service.stop()
        console.print("\nSaliendo...")

def main_rep(console):
    while True:
        baner(console)

        console.print(Panel('''[bold bright_white]
    1. Lista (carpeta)
    2. Playlist
    [bold white on red]0. Salir''', 
                            title='[black on #9999FF]Music Player', 
                            subtitle='[#9999FF]Mp3, m4a, flac, etc',
                            border_style='#9999FF'))
        s = Prompt.ask('Elije')
        if s=='0':
            break
        elif s=='1':
            run_player(console)
        elif s=='2':
            main_playlist(console)