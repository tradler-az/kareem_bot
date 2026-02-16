"""
Bosco Core - Wake Word Detection
Uses Snowboy for "Hey Bosco" / "Bosco" wake word detection
Falls back to simple audio detection if Snowboy unavailable
"""

import threading
import queue
import time
from typing import Callable, Optional, Dict, Any
import os

# Try to import snowboy, fall back to alternative
try:
    import snowboy.snowboydecoder as snowboydecoder
    SNOWBOY_AVAILABLE = True
except ImportError:
    SNOWBOY_AVAILABLE = False
    print("Snowboy not available. Using alternative wake word detection.")


class WakeWordDetector:
    """Wake word detection using Snowboy or alternative methods"""
    
    def __init__(self, wake_words: list = None, sensitivity: float = 0.5):
        self.wake_words = wake_words or ["bosco", "hey bosco"]
        self.sensitivity = sensitivity
        self.is_listening = False
        self.detected_callback: Optional[Callable] = None
        self.audio_queue = queue.Queue()
        self._detector = None
        self._thread = None
        
        # Alternative detection state
        self.energy_threshold = 500
        self.last_detection_time = 0
        self.cooldown_seconds = 2
        
        # Find model file
        self.model_path = self._find_model()
    
    def _find_model(self) -> str:
        """Find Snowboy model file"""
        possible_paths = [
            "voice/bosco_model.pmdl",
            "voice/bosco.umdl",
            "resources/bosco_model.pmdl",
            "bosco_model.pmdl",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default - will create if needed
        return "voice/bosco_model.pmdl"
    
    def create_model(self, hotword: str = "Bosco", output_path: str = None):
        """Create a Snowboy model file (requires training)"""
        # Note: Snowboy requires training models online
        # This is a placeholder for the workflow
        print(f"Model creation for '{hotword}' would require:")
        print("1. Go to https://snowboy.kitt.ai/")
        print("2. Record 3+ audio samples")
        print("3. Download and save the .pmdl file")
        
        if output_path:
            # Create empty placeholder
            with open(output_path, 'w') as f:
                f.write("# Snowboy model - needs to be trained at snowboy.kitt.ai")
        
        return output_path or self.model_path
    
    def start_listening(self, callback: Callable):
        """Start listening for wake word"""
        self.detected_callback = callback
        self.is_listening = True
        
        if SNOWBOY_AVAILABLE and os.path.exists(self.model_path):
            self._start_snowboy()
        else:
            self._start_alternative()
    
    def _start_snowboy(self):
        """Start Snowboy detection"""
        try:
            self._detector = snowboydecoder.HotwordDetector(
                self.model_path,
                sensitivity=self.sensitivity
            )
            
            def callback():
                if self.detected_callback:
                    self.detected_callback()
            
            self._thread = threading.Thread(
                target=self._detector.start,
                args=(callback,)
            )
            self._thread.daemon = True
            self._thread.start()
            print("Wake word detection active (Snowboy)")
            
        except Exception as e:
            print(f"Snowboy error: {e}. Using alternative.")
            self._start_alternative()
    
    def _start_alternative(self):
        """Start alternative keyword spotting using speech recognition"""
        import speech_recognition as sr
        
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self._microphone as source:
            print("Calibrating for ambient noise...")
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
            self.energy_threshold = self._recognizer.energy_threshold * 1.5
        
        self._thread = threading.Thread(target=self._alternative_listen, daemon=True)
        self._thread.start()
        print("Wake word detection active (Alternative mode)")
    
    def _alternative_listen(self):
        """Alternative listening using Google Speech Recognition"""
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        while self.is_listening:
            try:
                with self._microphone as source:
                    audio = recognizer.listen(
                        source,
                        phrase_time_limit=3,
                        timeout=1
                    )
                
                try:
                    # Try Google speech recognition
                    command = recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words
                    for wake_word in self.wake_words:
                        if wake_word in command:
                            current_time = time.time()
                            if current_time - self.last_detection_time > self.cooldown_seconds:
                                self.last_detection_time = current_time
                                if self.detected_callback:
                                    self.detected_callback()
                                break
                                
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
                    
            except Exception as e:
                time.sleep(0.1)
    
    def stop_listening(self):
        """Stop listening for wake word"""
        self.is_listening = False
        
        if self._detector:
            try:
                self._detector.stop()
            except:
                pass
        
        if self._thread:
            self._thread.join(timeout=2)
        
        print("Wake word detection stopped")
    
    def update_threshold(self, threshold: float):
        """Update detection sensitivity (0.0 to 1.0)"""
        self.sensitivity = max(0.0, min(1.0, threshold))


class WakeWordManager:
    """Manager for multiple wake words and detection modes"""
    
    def __init__(self):
        self.detector = WakeWordDetector()
        self.continuous_mode = False
        self.always_listening = False
        
    def activate(self, callback: Callable):
        """Activate wake word detection"""
        self.detector.start_listening(callback)
        
    def deactivate(self):
        """Deactivate wake word detection"""
        self.detector.stop_listening()
    
    def set_continuous_mode(self, enabled: bool):
        """Enable/disable continuous listening after wake word"""
        self.continuous_mode = enabled
    
    def set_always_listening(self, enabled: bool):
        """Enable/disable always listening mode"""
        self.always_listening = enabled


# Global instance
_wake_word_manager = WakeWordManager()


def start_wake_word(callback: Callable):
    """Start wake word detection"""
    _wake_word_manager.activate(callback)


def stop_wake_word():
    """Stop wake word detection"""
    _wake_word_manager.deactivate()


def set_continuous_mode(enabled: bool):
    """Set continuous mode"""
    _wake_word_manager.set_continuous_mode(enabled)


def set_always_listening(enabled: bool):
    """Set always listening mode"""
    _wake_word_manager.set_always_listening(enabled)


if __name__ == "__main__":
    print("Testing Wake Word Detection...")
    print("Say 'Bosco' or 'Hey Bosco' to activate")
    
    def on_wake():
        print(">>> WAKEDETECTED <<<")
    
    start_wake_word(on_wake)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_wake_word()
        print("Stopped.")

