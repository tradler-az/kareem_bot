"""
Bosco Core - Enhanced Speaker with JARVIS-like voice
Custom TTS with voice customization and sound effects
"""

import os
import threading
import queue
from typing import Optional, List
import time

# Try different TTS engines
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("pyttsx3 not available")

try:
    import gtts
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("gTTS not available")


class Speaker:
    """Enhanced TTS with JARVIS-like characteristics"""
    
    def __init__(self):
        self.engine = None
        self.queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        self.voice_speed = 200  # Words per minute
        self.voice_volume = 1.0
        self.voice_rate = 150   # pyttsx3 rate
        self.voice_id = 0       # Default voice
        
        # Initialize engine
        self._init_engine()
        
        # Sound effects
        self.sound_enabled = True
        self._init_sounds()
    
    def _init_engine(self):
        """Initialize TTS engine"""
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                
                # Get available voices
                voices = self.engine.getProperty('voices')
                if voices:
                    # Try to find a male/deep voice
                    for i, voice in enumerate(voices):
                        if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                            self.voice_id = i
                            break
                    
                    self.engine.setProperty('voice', voices[self.voice_id].id)
                
                # Set properties
                self.engine.setProperty('rate', self.voice_rate)
                self.engine.setProperty('volume', self.voice_volume)
                
                print("TTS Engine initialized (pyttsx3)")
                return
            except Exception as e:
                print(f"Error initializing pyttsx3: {e}")
        
        # Fallback to gTTS
        if GTTS_AVAILABLE:
            print("Using gTTS as fallback")
        else:
            print("Warning: No TTS engine available")
    
    def _init_sounds(self):
        """Initialize sound effects"""
        self.sounds = {
            "startup": "sounds/startup.wav",
            "listening": "sounds/listening.wav",
            "processing": "sounds/processing.wav",
            "success": "sounds/success.wav",
            "error": "sounds/error.wav",
            "shutdown": "sounds/shutdown.wav",
        }
        
        # Create sounds directory if needed
        for sound_path in self.sounds.values():
            sound_dir = os.path.dirname(sound_path)
            if sound_dir and not os.path.exists(sound_dir):
                os.makedirs(sound_dir, exist_ok=True)
    
    def play_sound(self, sound_name: str):
        """Play a sound effect"""
        if not self.sound_enabled:
            return
        
        sound_path = self.sounds.get(sound_name)
        if sound_path and os.path.exists(sound_path):
            try:
                # Try using playsound
                import subprocess
                subprocess.Popen(
                    ["aplay", sound_path] if os.uname().sysname == "Linux" 
                    else ["afplay", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                pass  # Silently fail if sound can't play
    
    def speak(self, text: str, blocking: bool = True):
        """Speak text with optional sound effects"""
        if not text:
            return
        
        # Add to queue for non-blocking
        if not blocking:
            self.queue.put(text)
            if not self.is_speaking:
                self._start_speaking_thread()
            return
        
        # Blocking speak
        self._speak_text(text)
    
    def _speak_text(self, text: str):
        """Actually speak the text"""
        self.is_speaking = True
        
        # Play processing sound for longer texts
        if len(text) > 100:
            self.play_sound("processing")
        
        if self.engine and PYTTSX3_AVAILABLE:
            try:
                # Adjust rate based on content
                original_rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', self.voice_rate)
                self.engine.say(text)
                self.engine.runAndWait()
                self.engine.setProperty('rate', original_rate)
            except Exception as e:
                print(f"TTS Error: {e}")
                # Fallback to gtts or system speak
                self._fallback_speak(text)
        else:
            self._fallback_speak(text)
        
        self.is_speaking = False
    
    def _fallback_speak(self, text: str):
        """Fallback TTS methods"""
        # Try gTTS
        if GTTS_AVAILABLE:
            try:
                tts = gtts.gTTS(text)
                tts.save("/tmp/bosco_speak.mp3")
                import subprocess
                subprocess.Popen(
                    ["mpg123", "-q", "/tmp/bosco_speak.mp3"] if os.uname().sysname == "Linux"
                    else ["afplay", "/tmp/bosco_speak.mp3"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
            except:
                pass
        
        # Last resort: espeak
        try:
            import subprocess
            subprocess.Popen(
                ["espeak", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except:
            print(f"Could not speak: {text}")
    
    def _start_speaking_thread(self):
        """Start background thread for speech queue"""
        if self.speech_thread and self.speech_thread.is_alive():
            return
        
        self.speech_thread = threading.Thread(target=self._speaking_worker, daemon=True)
        self.speech_thread.start()
    
    def _speaking_worker(self):
        """Worker for processing speech queue"""
        while True:
            try:
                text = self.queue.get(timeout=1)
                self._speak_text(text)
                self.queue.task_done()
            except queue.Empty:
                if self.queue.empty():
                    break
    
    def queue_speak(self, text: str):
        """Add text to speech queue"""
        self.speak(text, blocking=False)
    
    def interrupt(self):
        """Interrupt current speech"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        # Clear queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
        self.is_speaking = False
    
    # Voice customization
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.voice_rate = max(50, min(300, rate))
        if self.engine:
            self.engine.setProperty('rate', self.voice_rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.voice_volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.voice_volume)
    
    def set_voice(self, voice_index: int):
        """Set voice by index"""
        if self.engine:
            voices = self.engine.getProperty('voices')
            if 0 <= voice_index < len(voices):
                self.voice_id = voice_index
                self.engine.setProperty('voice', voices[voice_index].id)
    
    def get_voices(self) -> List[str]:
        """Get available voices"""
        if self.engine:
            return [v.name for v in self.engine.getProperty('voices')]
        return []
    
    def set_jarvis_voice(self):
        """Configure voice to sound more like JARVIS"""
        self.voice_rate = 170  # Slightly faster
        self.set_rate(self.voice_rate)
        
        # Try to find best matching voice
        voices = self.get_voices()
        for i, voice in enumerate(voices):
            if any(name in voice.lower() for name in ['male', 'david', 'zira']):
                self.set_voice(i)
                break
    
    def shutdown(self):
        """Clean shutdown"""
        self.interrupt()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


# Global speaker instance
_speaker = Speaker()


def speak(text: str, blocking: bool = True):
    """Quick speak function"""
    _speaker.speak(text, blocking)


def speak_async(text: str):
    """Speak non-blocking"""
    _speaker.speak(text, blocking=False)


def queue_speak(text: str):
    """Queue speech"""
    _speaker.queue_speak(text)


def interrupt():
    """Interrupt speech"""
    _speaker.interrupt()


def set_rate(rate: int):
    """Set speech rate"""
    _speaker.set_rate(rate)


def set_volume(volume: float):
    """Set volume"""
    _speaker.set_volume(volume)


def set_jarvis_voice():
    """Set JARVIS-like voice"""
    _speaker.set_jarvis_voice()


def play_sound(sound: str):
    """Play sound effect"""
    _speaker.play_sound(sound)


def get_speaker() -> Speaker:
    """Get speaker instance"""
    return _speaker


if __name__ == "__main__":
    print("Testing Bosco Speaker...")
    print(f"Available voices: {_speaker.get_voices()}")
    
    # Test speech
    speak("Bosco Core online. All systems nominal.")
    speak("This is a test of the text to speech system.")
    speak("I am now configured with a JARVIS-like voice.")
    set_jarvis_voice()
    speak("How may I assist you today?")

