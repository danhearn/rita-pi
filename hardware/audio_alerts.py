import os
import subprocess
from pathlib import Path


class AudioPlayer: 
    def __init__(self):
        # Get the absolute path to the sounds directory
        base_dir = Path(__file__).parent.parent
        self.warning_sound = os.path.join(base_dir, 'sounds', 'warning.mp3')
        self.success_sound = os.path.join(base_dir, 'sounds', 'success.mp3')
    
    def play_sound(self, sound_type):
        """Play a sound alert using aplay (ALSA)"""
        if sound_type == "warning":
            sound_file = self.warning_sound
        elif sound_type == "success":
            sound_file = self.success_sound
        else:
            return
        
        if not os.path.exists(sound_file):
            print(f"Sound file not found: {sound_file}")
            return
        
        try:
            # Use aplay (ALSA player) - more reliable on Raspberry Pi
            subprocess.Popen(['aplay', sound_file],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            # Fallback: try mpg123 if aplay not available
            try:
                subprocess.Popen(['mpg123', '-q', sound_file],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("Warning: Neither aplay nor mpg123 found. Install alsa-utils or mpg123.")
        except Exception as e:
            print(f"Error playing sound: {e}")