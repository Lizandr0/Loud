import os
from pathlib import Path

class AudioRepository:
    def __init__(self, folder="~/Música"):
        self.base_path = Path(folder).expanduser().resolve()
    
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, filename):
        file_path = self.base_path / filename
        if file_path.exists():
            return str(file_path.resolve())
        return None

    def list_mp3s(self):
        return [f.name for f in self.base_path.glob("*.mp3")]