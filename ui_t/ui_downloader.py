from textual.widgets import Input, Static, Footer, DataTable
from textual.app import ComposeResult
from textual.containers import Vertical,VerticalScroll, Horizontal

from services.services_yt import SearchService


from textual import work
class DownloaderView(Vertical):
    BINDINGS = [
        ("crl+q", "quit", "Salir"),
        ('1', 'ir_by_url', 'BY URL'),
        ('2', 'ir_playlist', 'PLAYLIST'),
        ('d', 'descargar', 'Descargar selección'),
        ('ctrl+x', 'limpiar', 'Limpiar todo'),
    ]
    CSS_PATH='styles.css'
    def compose(self) -> ComposeResult:
        with VerticalScroll(id='content_main'):
            yield Static("Busca y descarga desde [white on red]YouTube[/]", id="title-downloader")
            with Horizontal(id='content-inputs'):
                yield Input(placeholder="Busca tu video en YouTube", id="search_input")
                yield Input(placeholder='Cantidad de resultados a mostrar', id="results_input")
            with Vertical(id='content-tab'):
                yield DataTable(id="results_table")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search_input", Input).focus()
        tabla=self.query_one("#results_table", DataTable)
        tabla.cursor_type="row"
        tabla.add_columns("Título", "Duración", "URL")

    def on_show(self) -> None:
        tabla=self.query_one("#results_table", DataTable)
        tabla.clear()

        self.actualizar_tabla(tabla, [])
        
    def action_ir_playlist(self)-> None:
        from ui_t.ui_playlist import PlayList
        self.app.push_screen(PlayList())

    #accciones
    def action_ir_by_url(self)-> None:
        from ui_t.ui_by_url import ByUrl
        self.app.push_screen(ByUrl())

    def action_limpiar(self):
        self.query_one("#results_table", DataTable).clear()
        self.query_one('#search_input', Input).clear()
        self.query_one("#results_input", Input).clear()

        self.query_one('#search_input').focus()

    def action_descargar(self) -> None:
        tabla = self.query_one("#results_table", DataTable) 
        if tabla.cursor_row is not None:
            try:
                coordenadas = tabla.cursor_coordinate
                row_key, _ = tabla.coordinate_to_cell_key(coordenadas)
                fila = tabla.get_row(row_key)
                url = str(fila[2]).strip()

                self.notify(f"Iniciando descarga: {url}")   
                self.run_worker(
                    lambda: self.hilo_descarga(url),
                    exclusive=True,
                    thread=True   
                )
            except Exception as e:
                self.notify(f"Error al capturar la fila: {e}", severity="error")

    def actualizar_tabla(self, tabla, info):
        tabla.clear()
        for item in info:
            tabla.add_row(item['title'], f"{item['duration']}s", item['url'])

    def on_row_selected(self, row_index):
        tabla=self.query_one("#results_table", DataTable)
        url = tabla.get_row_by_index(row_index)[2]
        self.notify(f"Seleccionado: {url}")

        print(f"URL seleccionada: {url}")
        print(f'tipo de url: {type(url)}')

    def hilo_descarga(self, url: str) -> None:
        try:
            descarga = SearchService().descargar([url])
            
            if descarga.get("status") == "ok":
                mensaje_exito = descarga.get("message", "¡Descarga completada!")
                self.notify(mensaje_exito)
            else:
                mensaje_error = descarga.get("message", "Error desconocido")
                self.notify(f"Error: {mensaje_error}", severity="error")
                
        except Exception as e:
            self.notify(f"Error crítico en el hilo: {e}", severity="error")
    @work(thread=True)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id=='results_input':
            if not event.input.value.strip():
                event.input.value='1'
            self.query_one("#search_input", Input).focus()

        if event.input.id=='search_input':
            self.notify(f"Buscando: {event.value}")
            query = self.query_one("#search_input", Input).value
            cant_opciones = self.query_one("#results_input", Input).value
            if not query:
                self.notify("Por favor ingresa una consulta de búsqueda.")
                return
            if not cant_opciones.isdigit():
                self.notify("Por favor ingresa un número válido para la cantidad de resultados.")
                return
            cant_opciones = int(cant_opciones)

            self.notify(f"Buscando '{query}' con {cant_opciones} resultados...")

            resultado = SearchService().buscar_canciones(query, cant_opciones)

            self.notify(f"Resultados encontrados: {len(resultado)}")

            tabla=self.query_one("#results_table", DataTable)
            
            self.actualizar_tabla(tabla, resultado)