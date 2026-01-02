import os
from pathlib import Path
from playsound import playsound


class AudioPlayer: 
    def __init__(self):
        # Get the absolute path to the sounds directory
        base_dir = Path(__file__).parent.parent
        self.warning_sound = os.path.join(base_dir, 'sounds', 'warning.mp3')
        self.success_sound = os.path.join(base_dir, 'sounds', 'success.mp3')
    
    def play_sound(self, sound_type):
        """Play a sound alert"""
        if sound_type == "warning":
            if os.path.exists(self.warning_sound):
                playsound(self.warning_sound)
            else:
                print(f"Warning sound file not found: {self.warning_sound}")
        elif sound_type == "success":
            if os.path.exists(self.success_sound):
                playsound(self.success_sound)
            else:
                print(f"Success sound file not found: {self.success_sound}")