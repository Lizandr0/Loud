import asyncio
import json
import socket
import subprocess
import os
from pathlib import Path

class MPVPlayer:
    def __init__(self, ipc_socket: str = "/tmp/loud_mpv.sock"):
        self.ipc_socket = ipc_socket
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        if os.path.exists(self.ipc_socket):
            os.remove(self.ipc_socket)

        cmd = [
            "mpv",
            "--no-video",
            f"--input-ipc-server={self.ipc_socket}",
            "--idle",  
        ]
        self.process = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def send_keep_alive(self):
        comando = ["loadfile", "avsynth://test_src=sine:frequency=10:duration=1", "append-play"]
        self.send_command(comando)
        
    async def loop_keep_alive(self):
        while True:
            await asyncio.sleep(240)
            if self.is_idle(): 
                self.send_keep_alive()

    def send_command(self, command: list) -> None:
        if not os.path.exists(self.ipc_socket):
            return

        payload = json.dumps({"command": command}) + "\n"
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.ipc_socket)
            client.sendall(payload.encode("utf-8"))
            client.close()
        except Exception as e:
            print(f"Error al enviar comando a mpv: {e}")

    def play(self, target: str) -> None:

        ruta_o_url = str(Path(target).expanduser().resolve()) if not target.startswith("http") else target
        self.send_command(["loadfile", ruta_o_url, "replace"])

    def play_stream(self, url: str) -> None:
        self.play(url)

    def play_local(self, file_path: str) -> None:
        self.play(file_path)


    def toggle_pause(self) -> None:
        self.send_command(["cycle", "pause"])

    def stop(self) -> None:
        self.send_command(["stop"])
    
    def set_volume(self, level: int) -> None:
        self.send_command(["set_property", "volume", level])

    def quit(self) -> None:
        if self.process:
            self.send_command(["quit"])
            self.process.terminate()

    def get_property(self, property_name: str):
        if not os.path.exists(self.ipc_socket):
            return None

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(self.ipc_socket)
                payload = json.dumps({"command": ["get_property", property_name]}) + "\n"
                client.sendall(payload.encode("utf-8"))
                
                raw_data = client.recv(1024).decode("utf-8")
                data = json.loads(raw_data)
                
                if data.get("error") == "success":
                    return data.get("data")
                return None
        except Exception:
            return None

    def get_progress(self):
        current = self.get_property("time-pos") or 0
        total = self.get_property("duration") or 0
        return int(current), int(total)

    def is_idle(self) -> bool:
        idle = self.get_property("idle-active")
        return idle is True