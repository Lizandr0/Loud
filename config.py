import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.expanduser("~/.config/loud")
os.makedirs(CONFIG_DIR, exist_ok=True)

RUTAS_COOKIES = [
    os.path.join(CONFIG_DIR, "cookies.txt"),
    os.path.join(BASE_DIR, "data", "cookies.txt"),
    os.path.join(BASE_DIR, "cookies.txt"),
]


def resolver_cookies() -> str | None:
    for ruta in RUTAS_COOKIES:
        if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
            return ruta
    return None


COOKIES_PATH = resolver_cookies()

DB_PATH = os.path.join(CONFIG_DIR, "loud_db.db")

YTDLP_BIN = (
    shutil.which("yt-dlp")
    or os.path.join(BASE_DIR, "venv", "bin", "yt-dlp")
    or "/usr/share/loud/venv/bin/yt-dlp"
)