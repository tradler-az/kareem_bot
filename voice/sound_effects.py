"""
Bosco Core - Sound Effects
JARVIS-like sound effects for various actions
"""

import os
import subprocess
import threading
from typing import Optional
from pathlib import Path


class SoundEffects:
    """JARVIS-like sound effects player"""
    
    def __init__(self, sounds_dir: str = "sounds"):
        self.sounds_dir = Path(sounds_dir)
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Define sound effects
        self.sound_files = {
            # Startup/shutdown
            "startup": "startup.wav",
            "shutdown": "shutdown.wav",
            "standby": "standby.wav",
            
            # Listening
            "listening": "listening.wav",
            "processing": "processing.wav",
            
            # Feedback
            "success": "success.wav",
            "error": "error.wav",
            "warning": "warning.wav",
            
            # UI
            "click": "click.wav",
            "notification": "notification.wav",
            "beep": "beep.wav",
            
            # JARVIS-style
            "arc_reactor": "arc_reactor.wav",
            "hologram": "hologram.wav",
            "scanning": "scanning.wav",
        }
        
        # Check for sound playback capability
        self._check_audio()
    
    def _check_audio(self):
        """Check available audio players"""
        self.has_aplay = self._command_exists("aplay")
        self.has_afplay = self._command_exists("afplay")
        self.has_mpg123 = self._command_exists("mpg123")
        self.has_paplay = self._command_exists("paplay")
        
    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(
                ["which", cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return True
        except:
            return False
    
    def play(self, sound_name: str, async_play: bool = True):
        """Play a sound effect"""
        if sound_name not in self.sound_files:
            return
        
        filename = self.sound_files[sound_name]
        filepath = self.sounds_dir / filename
        
        # If file doesn't exist, generate or skip
        if not filepath.exists():
            # Generate simple beep as fallback
            self._generate_beep(filepath)
        
        if async_play:
            thread = threading.Thread(target=self._play_file, args=(str(filepath),), daemon=True)
            thread.start()
        else:
            self._play_file(str(filepath))
    
    def _play_file(self, filepath: str):
        """Play audio file with available player"""
        # Try various players
        players = []
        
        if os.uname().sysname == "Linux":
            if self.has_aplay:
                players.append(["aplay", filepath])
            if self.has_mpg123:
                players.append(["mpg123", "-q", filepath])
        elif os.uname().sysname == "Darwin":
            if self.has_afplay:
                players.append(["afplay", filepath])
        
        for player in players:
            try:
                subprocess.run(
                    player,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                return
            except:
                continue
    
    def _generate_beep(self, filepath: Path):
        """Generate a simple beep sound"""
        # Generate using sox or fallback
        try:
            # Try to generate with sox
            subprocess.run(
                ["sox", "-n", "-r", "44100", "-c", "1", str(filepath), "synth", "0.1", "sine", "1000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
        except:
            # Create empty file
            filepath.touch()
    
    def play_startup(self):
        """Play startup sound"""
        self.play("startup")
    
    def play_shutdown(self):
        """Play shutdown sound"""
        self.play("shutdown")
    
    def play_listening(self):
        """Play listening activation sound"""
        self.play("listening")
    
    def play_processing(self):
        """Play processing sound"""
        self.play("processing")
    
    def play_success(self):
        """Play success sound"""
        self.play("success")
    
    def play_error(self):
        """Play error sound"""
        self.play("error")
    
    def play_notification(self):
        """Play notification sound"""
        self.play("notification")
    
    def play_arc_reactor(self):
        """Play arc reactor sound"""
        self.play("arc_reactor")
    
    def play_scanning(self):
        """Play scanning sound"""
        self.play("scanning")


# Generate sound files using code (placeholder)
def generate_sounds(sounds_dir: str = "sounds"):
    """Generate basic sound files"""
    sounds_path = Path(sounds_dir)
    sounds_path.mkdir(exist_ok=True)
    
    # Try to generate using sox
    sounds = {
        "startup": ("synth", "2", "sine", "200:400"),
        "shutdown": ("synth", "2", "sine", "400:200"),
        "listening": ("synth", "0.1", "sine", "800"),
        "processing": ("synth", "0.05", "sine", "600"),
        "success": ("synth", "0.2", "sine", "1000"),
        "error": ("synth", "0.3", "sine", "200"),
        "beep": ("synth", "0.1", "sine", "440"),
    }
    
    for name, args in sounds.items():
        filepath = sounds_path / f"{name}.wav"
        try:
            subprocess.run(
                ["sox", "-n", "-r", "44100", "-c", "1", str(filepath)] + list(args),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            print(f"Generated: {filepath}")
        except Exception as e:
            print(f"Could not generate {name}: {e}")


# Global instance
_sound_effects = SoundEffects()


def play(sound_name: str):
    """Quick play function"""
    _sound_effects.play(sound_name)


def play_startup():
    """Play startup sound"""
    _sound_effects.play_startup()


def play_shutdown():
    """Play shutdown sound"""
    _sound_effects.play_shutdown()


def play_listening():
    """Play listening sound"""
    _sound_effects.play_listening()


def play_processing():
    """Play processing sound"""
    _sound_effects.play_processing()


def play_success():
    """Play success sound"""
    _sound_effects.play_success()


def play_error():
    """Play error sound"""
    _sound_effects.play_error()


def play_notification():
    """Play notification sound"""
    _sound_effects.play_notification()


def get_sound_effects() -> SoundEffects:
    """Get sound effects instance"""
    return _sound_effects


if __name__ == "__main__":
    print("Testing Sound Effects...")
    
    # Generate sounds if sox available
    print("Generating sound files...")
    generate_sounds()
    
    # Test playback
    print("Playing test sounds...")
    play_startup()
    import time
    time.sleep(1)
    play_listening()
    time.sleep(0.5)
    play_processing()
    time.sleep(0.5)
    play_success()

