import vlc
import time

import vlc
import time

class PlayerService:
    def __init__(self):
        self.instance = vlc.Instance('--quiet')
        self.player = self.instance.media_player_new()

    def play(self, path):
        if not path:
            return False
        
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        
        time.sleep(0.2)
        return True

    def toggle_pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def get_status(self):
        ms_actual = self.player.get_time()
        ms_total = self.player.get_length()
        
        return {
            "current": ms_actual // 1000 if ms_actual > 0 else 0,
            "total": ms_total // 1000 if ms_total > 0 else 0,
            "is_playing": self.player.is_playing()
        }