"""
Bosco Core - Enhanced Voice Listener
Advanced voice recognition with noise handling and multiple listening modes
"""

import time
import threading
import queue
from typing import Optional, Callable, List
import re

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("speech_recognition not available")


class Listener:
    """Enhanced voice listener with multiple modes"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.listen_thread = None
        
        # Configuration
        self.energy_threshold = 300  # Minimum audio energy to consider
        self.pause_threshold = 0.8  # Seconds of silence to consider phrase complete
        self.phrase_threshold = 0.3  # Minimum seconds of speaking
        self.phrase_time_limit = 10  # Maximum phrase length
        
        # Continuous listening
        self.continuous_queue = queue.Queue()
        self.continuous_callback: Optional[Callable] = None
        
        # Initialize
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Initialize speech recognizer and microphone"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return
        
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.phrase_threshold = self.phrase_threshold
        
        # Get microphone
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Microphone error: {e}")
    
    def calibrate(self, duration: float = 1.0):
        """Calibrate for ambient noise"""
        if not self.microphone or not self.recognizer:
            return
        
        with self.microphone as source:
            print(f"Calibrating for {duration} seconds...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.energy_threshold = self.recognizer.energy_threshold
            print(f"Energy threshold set to: {self.energy_threshold}")
    
    def listen(self, timeout: float = 5.0, phrase_time_limit: float = None) -> str:
        """Listen for a single phrase"""
        if not self.microphone or not self.recognizer:
            return ""
        
        if phrase_time_limit is None:
            phrase_time_limit = self.phrase_time_limit
        
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize using Google
            command = self.recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return ""
        except sr.UnknownValueError:
            print("Speech not understood")
            return ""
        except sr.RequestError as e:
            print(f"Recognition service error: {e}")
            return ""
    
    def listen_with_confirmation(self) -> str:
        """Listen and confirm with user"""
        command = self.listen()
        
        if command:
            # Could add confirmation step here
            pass
        
        return command
    
    def listen_continuous(self, callback: Callable[[str], None], stop_event: threading.Event):
        """Continuously listen for commands"""
        self.continuous_callback = callback
        
        while not stop_event.is_set():
            try:
                command = self.listen(timeout=3)
                if command:
                    callback(command)
            except Exception as e:
                print(f"Continuous listening error: {e}")
                time.sleep(0.5)
    
    def start_continuous(self, callback: Callable[[str], None]):
        """Start continuous listening in background"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.stop_event = threading.Event()
        
        self.listen_thread = threading.Thread(
            target=self.listen_continuous,
            args=(callback, self.stop_event),
            daemon=True
        )
        self.listen_thread.start()
    
    def stop_continuous(self):
        """Stop continuous listening"""
        self.is_listening = False
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
    
    def adjust_threshold(self, multiplier: float = 1.5):
        """Adjust energy threshold based on ambient noise"""
        if self.recognizer:
            self.recognizer.energy_threshold *= multiplier
    
    # Intent-based listening
    def listen_for_keywords(self, keywords: List[str], timeout: float = 10.0) -> Optional[str]:
        """Listen until one of the keywords is detected"""
        if not self.microphone or not self.recognizer:
            return None
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1)
                
                text = self.recognizer.recognize_google(audio).lower()
                
                for keyword in keywords:
                    if keyword.lower() in text:
                        return keyword
                        
            except:
                continue
        
        return None
    
    # Audio level monitoring
    def get_audio_level(self) -> float:
        """Get current audio level (0.0 to 1.0)"""
        if not self.microphone or not self.recognizer:
            return 0.0
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, phrase_time_limit=0.1)
            
            # Calculate energy
            import numpy as np
            audio_data = audio.get_raw_data()
            energy = sum(bytes(audio_data)) / len(audio_data) if audio_data else 0
            return min(1.0, energy / 255.0)
            
        except:
            return 0.0
    
    def wait_for_silence(self, threshold: float = 0.1, timeout: float = 5.0) -> bool:
        """Wait for silence"""
        start = time.time()
        
        while time.time() - start < timeout:
            level = self.get_audio_level()
            if level < threshold:
                return True
            time.sleep(0.1)
        
        return False
    
    def wait_for_sound(self, threshold: float = 0.3, timeout: float = 5.0) -> bool:
        """Wait for sound above threshold"""
        start = time.time()
        
        while time.time() - start < timeout:
            level = self.get_audio_level()
            if level > threshold:
                return True
            time.sleep(0.1)
        
        return False


# Global listener instance
_listener = Listener()


def listen(timeout: float = 5.0) -> str:
    """Quick listen function"""
    return _listener.listen(timeout)


def listen_continuous(callback: Callable[[str], None]):
    """Start continuous listening"""
    _listener.start_continuous(callback)


def stop_listening():
    """Stop continuous listening"""
    _listener.stop_continuous()


def calibrate(duration: float = 1.0):
    """Calibrate microphone"""
    _listener.calibrate(duration)


def get_listener() -> Listener:
    """Get listener instance"""
    return _listener


# Convenience function for main.py compatibility
def listen_for_command(timeout: float = 5.0) -> str:
    """Listen for a voice command (compatibility function)"""
    return _listener.listen(timeout=timeout)


if __name__ == "__main__":
    print("Testing Bosco Listener...")
    
    # Calibrate
    calibrate(2)
    
    # Test listening
    print("Say something:")
    result = listen()
    print(f"Result: {result}")

