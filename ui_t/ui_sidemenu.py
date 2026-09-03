from textual.widgets import Label, OptionList, Static, DataTable, Footer
from textual.widgets.option_list import Option
from textual.containers import Vertical
from textual.app import ComposeResult
import uuid
from textual import work
from services.services_sqlite import sqliteService
from ui_t.ui_local_music import LocalMusicView
class Sidebar(Vertical):

    BINDINGS=[
        ("ctrl+d", "delete_playlist", "Eliminar Playlist"),
    ]
    def compose(self) -> ComposeResult:
        yield Label("LOUD TUI", id="sidebar-title")
        with Vertical():
            yield OptionList(
                Option("▶ Reproductor", id="nav_player_"),
                Option("⬇ Descargador", id="nav_downloader"),
                id="menu_list",
            )
        with Vertical(id='content-playlists'):
            yield DataTable(id='table-playlists')

        with Vertical(id='container-local-music'):
            yield Static('Música Local', id='title-local-music')
            yield  LocalMusicView()
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries=sqliteService()
    @work
    async def action_delete_playlist(self)->None:
        from ui_t.ui_messagebox import Msg
        validar=await self.app.push_screen_wait(Msg('Eliminar Playlist?'))
        if validar:
            tabla = self.query_one("#table-playlists", DataTable)
            if tabla.cursor_row is None or tabla.row_count == 0:
                self.notify(
                    "Selecciona una playlist para eliminar", severity="warning"
                )
                return
            row_key, _ = tabla.coordinate_to_cell_key(tabla.cursor_coordinate)
            row_key_str = str(row_key.value) if row_key else ""

            if row_key_str.startswith("pl_"):
                playlist_id = int(row_key_str.replace("pl_", ""))

                self.queries.eliminar_playlist(playlist_id)

                tabla.remove_row(row_key)

                self.notify(
                    f"Playlist ID {playlist_id} eliminada", title="LOUD"
                )
        else:
            self.notify('Cancelado por el usuario!')
               
        
    def actualizar_tabla_playlists(self):
        tabla=self.query_one("#table-playlists", DataTable)
        info=self.queries.obtener_playlist()
        tabla.clear()
        if info:
            for i in info:
                tabla.add_row(
                    f'🎜 {i[1]}',
                    key=f'pl_{i[0]}',
                    )
        else:
            tabla.add_row('Vacio')

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "table-playlists":
            row_key = str(event.row_key.value) if event.row_key else ""
            
            if row_key.startswith("pl_"):
                playlist_id = int(row_key.replace("pl_", ""))
                self.app.id_playlist=playlist_id
                
                try:
                    player = self.app.query_one("#nav_player_")
                    
                    player.cargar_playlist_a_cola(playlist_id)

                    self.notify(f"Cargando playlist: {playlist_id}...")
                except Exception as e:
                    self.notify(f"Error al buscar player: {e}", severity="error")
            else:
                self.notify(f"Fila sin formato pl_: {row_key}", severity="warning")

    def _on_mount(self)->None:
        tabla=self.query_one("#table-playlists", DataTable)
        tabla.cursor_type = "row"
        tabla.add_column('Playlists')
        self.actualizar_tabla_playlists()

    def _on_show(self)->None:
        self.actualizar_tabla_playlists()