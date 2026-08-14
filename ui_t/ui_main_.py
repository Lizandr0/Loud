from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    Header,
    Footer,
    OptionList,
    ContentSwitcher,
    DataTable
)
from ui_t.ui_player import PlayerView
from ui_t.ui_downloader import DownloaderView
from ui_t.ui_sidemenu import Sidebar

class LoudApp(App):
    def __init__(self):
        super().__init__()
        self.id_playlist=''
        self.queue = []

        variables_css = self.app.get_css_variables()
        self.color_accent = variables_css.get("accent", "green")
        
    CSS_PATH = "../ui_t/styles.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id='main-cont'):
            yield Sidebar(id="sidebar")
            with ContentSwitcher(initial="nav_player_", id="main_content"):
                yield PlayerView(id="nav_player_")
                yield DownloaderView(id="nav_downloader")
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        switcher = self.query_one("#main_content", ContentSwitcher)
        if event.option_id:
            switcher.current = event.option_id