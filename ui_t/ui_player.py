from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    DataTable,
    Select
)
import uuid
import asyncio

from services.services_yt import SearchService as YTService
from services.services_player_mpv import MPVPlayer
from services.services_sqlite import guardar_cola, obtener_canciones, actualizar_playist
from services.services_yt import SearchService
from textual import work
class SplitBalancePlayer(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Buscar Canciones", classes="section_title")
        with Vertical(id="header-search"):
            with Horizontal(id="search-zone"):
                yield Select(
                    options=[
                        ("Canción", "song"),
                        ("Playlist YT", "yt_playlist")
                    ],
                    value="song",
                    id="select_search_mode",
                    allow_blank=False
                )
                
                yield Input(
                        placeholder="Buscar canción para añadir a la cola...",
                        id="search_input_",
                    )
            
                yield DataTable(id="table-search")

        yield Label("Cola de Reproducción", id="mid-zone-title")
        with VerticalScroll(id="mid-zone"):
            yield DataTable(id="table-cola")

        with Horizontal(id="player_bar"):
            yield Label("Resonance — HOME", id="now_playing_info")

            with Horizontal(id="progress_block"):
                yield Label("---", id="time_current")
                yield ProgressBar(
                    total=212, show_percentage=False, show_eta=False, id="time_bar"
                )
                yield Label("----", id="time_total")
                
            with Horizontal(id="controls_mini"):
                yield Button("⏮", id="btn_prev")
                yield Button("⏸", id="btn_pause")
                yield Button("⏭", id="btn_next")

class PlayerView(Vertical):
    BINDINGS = [
            ("space", "toggle_pause", "Play/Pausa"),
            ("l", "seek_forward", "+10s"),
            ("h", "seek_backward", "-10s"),
            ("n", "next", "Siguiente"),
            ("p", "prev", "Anterior"),
            ("delete", "delete_from_queue","Eliminar de la cola"),
            ("ctrl+g", "save_cola", "Guardar la cola"),
            ("ctrl+u", "update_playlist", "Actualizar Playlist"),
            ("ctrl+l", "delete_cola", "Limpiar cola"),
        ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = None  
        self.queue=self.app.queue       
        self.current_index = -1  
        self.is_playing = False

        self.service=SearchService()
    

    def compose(self) -> ComposeResult:
        yield SplitBalancePlayer()
        yield Footer()

    def on_mount(self) -> None:
        self.player=MPVPlayer()
        self.player.start()

        asyncio.create_task(self.player.loop_keep_alive())

        self.query_one("#search_input_", Input).focus()

        self.progress_bar = self.query_one("#time_bar", ProgressBar)
        self.set_interval(1.0, self.update_playback_progress)


        tabla_search=self.query_one("#table-search", DataTable)
        tabla_search.zebra_stripes=False
        tabla_search.cursor_type="row"
        tabla_search.add_columns("Resultado de la busqueda:", " ", "   ")
        self.actualizar_tabla_busqueda(tabla_search, [])

        tabla_cola=self.query_one("#table-cola", DataTable)
        tabla_cola.zebra_stripes=True
        tabla_cola.cursor_type="row"
        tabla_cola.add_columns("Título", "Duracion", "URL")

        self.reproduciendo_cancion("Ninguna canción en reproducción")
    
    def on_unmount(self) -> None:
        self.player.quit()

    def _on_show(self)-> None:
        tabla=self.query_one("#table-search", DataTable)
        self.actualizar_tabla_busqueda(tabla, [])

    #acciones - BINDINGS
    def action_next(self)->None:
        self.play_next_song()
        
    def action_prev(self)->None:
        self.play_prev_song()

    def action_delete_cola(self)->None:
        tabla=self.query_one("#table-cola", DataTable)
        tabla.clear()
        self.app.id_playlist=''
        self.app.queue.clear()
        self.notify('Cola de reproduccion eliminada!', title="LOUD", severity='warning')
        
    @work
    async def action_update_playlist(self)->None:
        self.notify(f"Actualizando Playlist: {self.app.id_playlist}", title='LOUD', severity='information')

        from ui_t.ui_messagebox import Msg
        validar=await self.app.push_screen_wait(Msg(f'Guardar cambios en la Playlist {self.app.id_playlist}'))
        if validar:
            try:
                actualizar_playist(self.app.id_playlist, self.queue)
                self.notify(f"La Playlist: {self.app.id_playlist} fue actualizada!", title="LOUD", severity='information')
            except Exception as e:
                self.notify(f"Error al actualizar, {e}", title='LOUD', severity='error')
        else:
            self.notify('Cancelado por el usuario!', title="LOUD", severity='warning')

    def action_delete_from_queue(self) -> None:
        queue_table = self.query_one("#table-cola", DataTable)
        if not self.queue or queue_table.cursor_row is None:
            return
        row_index = queue_table.cursor_row

        if row_index < 0 or row_index >= len(self.queue):
            return
        removed_song = self.queue.pop(row_index)
        row_keys = list(queue_table.rows.keys())
        if row_index < len(row_keys):
            queue_table.remove_row(row_keys[row_index])
        if row_index == self.current_index:
            self.notify(f"Eliminada (reproduciendo): {removed_song['title']}", title='LOUD', severity='warning')

            self.current_index -= 1

            if self.queue:
                self.play_next_song()
            else:
                self.player.send_command(["stop"])
                self.is_playing = False
                self.current_index = -1
                self.query_one("#now_playing_info", Label).update(
                    "Sin reproducción"
                )
        elif row_index < self.current_index:
            self.current_index -= 1
            self.notify(f"Eliminada de la cola: {removed_song['title']}", title="LOUD", severity='warning')
        else:
            self.notify(f"Eliminada de la cola: {removed_song['title']}", title="LOUD", severity='warning')

    @work
    async def action_save_cola(self) -> None:
        from ui_t.ui_guardar_cola_box import SaveCola
        playlist_name = await self.app.push_screen_wait(SaveCola())
        if not playlist_name:
            return
        if not self.queue:
            self.notify("¡La lista está vacía!", severity="warning", title='LOUD')
            return
        try:
            guardar_cola(playlist_name, self.queue)
            self.notify(f"Playlist '{playlist_name}' guardada con éxito", title="LOUD", severity='information')
            sidebar = self.app.query_one("#sidebar")
            sidebar.actualizar_tabla_playlists()
        except Exception as e:
            self.notify(f"Error al guardar: {e}", severity="error", title="LOUD")
         
    def action_toggle_pause(self) -> None:
        self.notify("Pausando/Reanudando reproducción...")
        self.player.toggle_pause()
    
    def action_seek_forward(self) -> None:
        self.player.send_command(["seek", 10])
    
    def action_seek_backward(self) -> None:
        self.player.send_command(["seek", -10])
    
    #eventos de los widgets
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn_pause":
            self.notify("Pausando/Reanudando reproducción...")
            self.player.toggle_pause()

        elif button_id=='btn_next':
            self.notify('Reproduciendo siguiente cancion...')
            self.play_next_song()

        elif button_id=="btn_prev":
            self.notify('Reproduciendo la cancion anterior...')
            self.play_prev_song()

    @work(thread=True)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            self.notify("Por favor, ingresa un término de búsqueda o una URL.", title='LOUD', severity='error')
            return
        modo=self.query_one('#select_search_mode', Select).value
        if modo =='song':
            self.notify(f"Buscando {query}...", title='LOUD')
            service = YTService()
            resultados = service.buscar_canciones_stream(query)
            if resultados:
                tabla=self.query_one("#table-search", DataTable)
                self.actualizar_tabla_busqueda(tabla, resultados)
                self.notify(f"Resultados para {query} encontrados!", title="LOUD", severity='information')
                self.query_one("#search_input_", Input).clear()
            else:
                self.notify(f"No se encontraron resultados para {query}", title='LOUD', severity='warning')
                self.query_one("#search_input_", Input).clear()

        elif modo == 'yt_playlist':
            self.notify(f"Buscando canciones en: {query}")
            if self.search_playlist(query):
                self.notify("Ya Puedes guardar la playlist!", title='LOUD')
            else:
                return

    def search_playlist(self, url):
        songs=self.service.buscar_playlist(url)
        queue_table = self.query_one("#table-cola", DataTable)

        if songs is None:
            self.notify("No se encontraron canciones!", title='LOUD', severity='error')
            self.query_one("#search_input_", Input).clear()
            return
            
        if songs:
            self.app.queue.clear()
            self.action_delete_cola()
            for song in songs:
                self.app.queue.append(song)
                unique_key = f"{uuid.uuid4().hex[:6]}_{song['url']}"
                queue_table.add_row(song['title'], f"{song['duration']}ss", song['url'], key=unique_key)
            self.notify(f'Playlist encontrada, se cargaron {len(songs)} canciones a la cola!', title='LOUD')
            self.query_one("#search_input_", Input).clear()
        else:
            self.notify(f"No se encontraron canciones en {url}!", title='LOUD', severity='warning')
            self.query_one("#search_input_", Input).clear()

    def update_playback_progress(self) -> None:
        if self.is_playing and self.player.is_idle():
            self.is_playing = False
            self.play_next_song()
            return
    
        current, total = self.player.get_progress()
        if total > 0:
            self.progress_bar.total = total
            self.progress_bar.progress = current
    
            self.query_one("#time_current", Label).update(self.format_time(current))
            self.query_one("#time_total", Label).update(self.format_time(total))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table_id = event.data_table.id
        if table_id == "table-search":
            results_table = event.data_table
            row_data = results_table.get_row(event.row_key)
            title, duration, url = row_data[0].replace("🎜", "").strip(), row_data[1], row_data[2]
    
            song = {"title": title, "duration": duration, "url": url}
            self.app.queue.append(song)
    
            unique_key = f"{uuid.uuid4().hex[:6]}_{url}"
            queue_table = self.query_one("#table-cola", DataTable)
            queue_table.add_row(title, duration, url, key=unique_key)
    
            self.notify(f"Añadido a la cola: {title}", title="LOUD")
    
            if not self.is_playing:
                self.play_next_song()
    
        elif table_id == "table-cola":
            self.current_index = event.cursor_row
            song = self.app.queue[self.current_index]
    
            self.player.play_stream(song["url"])
            self.reproduciendo_cancion(song["title"])
            self.is_playing = True

    #otras fucniones alv
    def cargar_playlist_a_cola(self, playlist_id: int) -> None:
        canciones = obtener_canciones(playlist_id)
        if not canciones:
            self.notify(
                "La playlist está vacía o no se pudo leer", severity="warning", title='LOUD'
            )
            return
        self.queue.clear()
        tabla_cola = self.query_one("#table-cola", DataTable)
        tabla_cola.clear()

        for song in canciones:
            self.app.queue.append(song)
            tabla_cola.add_row(
                f"🎜 {song["title"]}",
                f"{song['duration']}s",
                song["url"],
                key=f"song_{uuid.uuid4().hex[:6]}",
            )
        self.notify(
            f"Cargadas {len(canciones)} canciones a la cola", title="LOUD"
        )

    @staticmethod
    def format_time(seconds: int) -> str:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def reproduciendo_cancion(self, url: str) -> None:
        self.query_one("#now_playing_info", Label).update(f"Reproduciendo: {url}")

    def actualizar_tabla_busqueda(self, tabla, info):
        tabla.clear()
        for item in info:
            tabla.add_row(item['title'], f"{item['duration']}s", item['url'])

    def play_next_song(self) -> None:
        if self.current_index + 1 < len(self.queue):
            self.current_index += 1
            next_song = self.queue[self.current_index]

            # 1. Le avisamos a la clase del reproductor que ignore el próximo 'end-file'
            # (ya que la interrupción fue provocada a propósito por la App)
            self.player.ignorar_siguiente_eof = True

            # 2. Reemplazamos la canción en mpv especificando "replace"
            self.player.send_command(["loadfile", next_song["url"], "replace"])
            self.is_playing = True

            self.update_queue_ui()
            self.reproduciendo_cancion(next_song["title"])
        else:
            self.notify("Cola de reproducción finalizada", title='LOUD')
            self.reproduciendo_cancion('No hay reproduccion activa')

    def play_prev_song(self) -> None:
        if self.current_index - 1 < len(self.queue):
            self.current_index -= 1
            next_song = self.queue[self.current_index]  
            self.player.send_command(["loadfile", next_song["url"]])
            self.is_playing = True  
            self.update_queue_ui()
            self.reproduciendo_cancion(next_song["title"])
        else:
            self.notify("Cola de reproducción finalizada", title='LOUD')
            self.reproduciendo_cancion('No hay reproduccion activa')

    def update_queue_ui(self) -> None:
        queue_table = self.query_one("#table-cola", DataTable)
        queue_table.move_cursor(row=self.current_index)