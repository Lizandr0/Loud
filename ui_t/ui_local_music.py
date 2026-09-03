from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option
from textual.widget import Widget
import uuid
import subprocess
class LocalMusicView(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rutas_carpetas: list[Path] = []

    def compose(self) -> ComposeResult:
        yield OptionList(id="folders_list")

    def on_mount(self) -> None:
        self.cargar_carpetas()

    def cargar_carpetas(self) -> None:
        ruta_base = Path("~/Música").expanduser()
        lista_carpetas = self.query_one("#folders_list", OptionList)
        lista_carpetas.clear_options()
        self.rutas_carpetas.clear()

        lista_carpetas.add_option(Option("Toda la Música"))
        self.rutas_carpetas.append(ruta_base)

        extensiones = {".mp3", ".flac", ".m4a", ".opus", ".ogg", ".wav"}
        carpetas = set()

        if ruta_base.exists():
            for archivo in ruta_base.rglob("*"):
                if archivo.is_file() and archivo.suffix.lower() in extensiones:
                    carpetas.add(archivo.parent)

        for folder in sorted(carpetas):
            try:
                nombre_relativo = str(folder.relative_to(ruta_base))
            except ValueError:
                nombre_relativo = folder.name
            
            lista_carpetas.add_option(Option(f"🗁  {nombre_relativo}"))
            self.rutas_carpetas.append(folder)
   
    def obtener_ruta_musica(self) -> Path:
        try:
            ruta_xdg = subprocess.check_output(
                ['xdg-user-dir', 'MUSIC'],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            
            if ruta_xdg:
                path_xdg = Path(ruta_xdg).expanduser().resolve()
                if path_xdg.exists():
                    return path_xdg
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        home = Path.home()
        for nombre_carpeta in ["Música", "Music", "musica", "music"]:
            posible_ruta = home / nombre_carpeta
            if posible_ruta.exists():
                return posible_ruta.resolve()

        ruta_defecto = home / "Música"
        ruta_defecto.mkdir(parents=True, exist_ok=True)
        return ruta_defecto

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        indice = event.option_index
        folder_id = self.rutas_carpetas[indice]

        if indice == 0:
            self.notify("Seleccionadas todas las canciones")
        else:
            self.notify(f"Carpeta activa: {folder_id.name if isinstance(folder_id, Path) else folder_id}")

        canciones_encontradas = []
        
        tabla = self.app.query_one("#table-cola")
        tabla.clear()

        extensiones = {".mp3", ".flac", ".m4a", ".opus", ".ogg", ".wav"}
        
        ruta_base = self.obtener_ruta_musica()

        if folder_id == "Toda la musica" or indice == 0:
            archivos = ruta_base.rglob("*")
        else:
            archivos = folder_id.iterdir()

        for archivo in archivos:
            if archivo.is_file() and archivo.suffix.lower() in extensiones:
                canciones_encontradas.append(archivo)
        canciones_encontradas.sort(key=lambda x: x.name.lower())

        self.app.queue.clear()

        for archivo in canciones_encontradas:
            song_dict = {
                "title": archivo.stem,
                "duration": "--:--",
                "url": str(archivo.resolve())
            }
            self.app.queue.append(song_dict)
            unique_key = f"{uuid.uuid4().hex[:6]}_{archivo.resolve()}"

            tabla.add_row(f"🎜 {archivo.stem}", "--:--", str(archivo.resolve()), key=unique_key)

        cantidad = len(canciones_encontradas)
        self.notify(f"Se añadieron {cantidad} canciones a la cola")