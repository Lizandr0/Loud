from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
import os

from ui.ui_banner import baner
from services.services_buscarenyt import SearchService


def seleccionar_urls(console, max_op):
    while True:
        entrada = Prompt.ask(
            "Selecciona opciones (ej: 1,3,5) o 0 para cancelar"
        ).strip()

        if entrada == "0":
            return 

        try:
            seleccion = [int(x) for x in entrada.split(",")]
            if all(1 <= x <= max_op for x in seleccion):
                return seleccion
        except ValueError:
            pass

        console.print("[red]Selección inválida. Intenta de nuevo.[/red]")

def tabla_resultados(console, resultado):
    tabla=Table(border_style='#9999FF')
    tabla.add_column('No.')
    tabla.add_column('Cancion')
    tabla.add_column('Duracion')
    for i, r in enumerate(resultado, 1):
        tabla.add_row(str(i), r['title'], f"{r['duration']}s")
    console.print(tabla)

def buscar_y_descargar(console, service):
    #pedir datos
    query=Prompt.ask("[bold #FF0000]Nombre de la cancion o artista")
    while True:
        try:
            cant_opciones=IntPrompt.ask("[bold #FF0000]Cuantas deseas ver")
            if cant_opciones==0:
                console.print(F'[bold bright_black on yellow]NO PUEDES BUSCAR [green]{cant_opciones}[/] OPCIONES')
            else:
                break
        except ValueError:
            console.print('Ingresa un valor entero!!', style='black on red')

    #mostrar resultados
    resultado=service.buscar_canciones(query, cant_opciones)
    tabla_resultados(console, resultado)

    #seleccionar de resultados
    seleccion=seleccionar_urls(console,len(resultado))
    if not seleccion:
        return
    urls = [resultado[i - 1]["url"] for i in seleccion]

    console.print("\n[bold green]Seleccionaste:[/bold green]")
    for url in urls:
        console.print(f"{url}")

    #descargar
    descargado=service.descargar(urls)
    if descargado["status"] == "ok":
        console.print(descargado["message"])
        for r in descargado["data"]:
            console.print(r["title"])
    else:
        console.print(descargado["message"])

    input('->')

def main_descargar(console):
    service=SearchService()
    
    while True:
        baner(console)

        console.print(Panel('''
    1. Buscar
    0. Cancelar y regresar
                      ''', title='Buscar y descargar de [white on red]YouTube'))
        s=Prompt.ask('-->')
        if s=='0':
            break
        elif s=='1':
            buscar_y_descargar(console, service)
        else:
            console.print('Intenta de nuevo!', style='black on red')
            input('->')