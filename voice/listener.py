"""
Bosco Core - Enhanced Voice Listener
Advanced voice recognition with noise handling and multiple listening modes
"""

import os
import sys
import io
import warnings

# Suppress ALSA and JACK warnings at import time
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('JACK_NO_AUDIO_RESERVATION', '1')
os.environ.setdefault('JACK_NO_START_SERVER', '1')

# Suppress stderr temporarily during critical imports
_OLD_STDERR = sys.stderr
sys.stderr = io.StringIO()

import time
import threading
import queue
import json
from typing import Optional, Callable, List
import re

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("speech_recognition not available")

# Restore stderr but keep error messages
_captured_stderr = sys.stderr.getvalue()
sys.stderr = _OLD_STDERR

# Log errors at debug level only
if _captured_stderr:
    import logging
    logging.getLogger(__name__).debug(f"Audio init messages: {_captured_stderr[:200]}...")


def load_config():
    """Load configuration from config.json"""
    for path in ['config.json', 'bosco_os/config.json']:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    return {}


# Load config for voice settings
_config = load_config()
_voice_config = _config.get('voice', {})


class Listener:
    """Enhanced voice listener with multiple modes"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.listen_thread = None
        
        # Configuration - loaded from config.json with defaults
        self.energy_threshold = _voice_config.get('energy_threshold', 300)
        self.pause_threshold = _voice_config.get('pause_threshold', 0.8)
        self.phrase_threshold = 0.3  # Minimum seconds of speaking
        self.listen_timeout = _voice_config.get('listen_timeout', 5.0)
        self.phrase_time_limit = _voice_config.get('phrase_time_limit', 10.0)
        self.calibration_duration = _voice_config.get('calibration_duration', 1.0)
        
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
        
        # Get microphone - suppress ALSA/Jack warnings during init
        try:
            import io
            import sys
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                self.microphone = sr.Microphone()
            finally:
                sys.stderr = old_stderr
        except Exception as e:
            print(f"Microphone error: {e}")
    
    def set_timeouts(self, listen_timeout: float = None, phrase_time_limit: float = None):
        """Update timeout settings dynamically"""
        if listen_timeout is not None:
            self.listen_timeout = listen_timeout
        if phrase_time_limit is not None:
            self.phrase_time_limit = phrase_time_limit
    
    def calibrate(self, duration: float = None):
        """Calibrate for ambient noise"""
        if duration is None:
            duration = self.calibration_duration
            
        if not self.microphone or not self.recognizer:
            return
        
        with self.microphone as source:
            print(f"Calibrating for {duration} seconds...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.energy_threshold = self.recognizer.energy_threshold
            print(f"Energy threshold set to: {self.energy_threshold}")
    
    def listen(self, timeout: float = None, phrase_time_limit: float = None) -> str:
        """Listen for a single phrase"""
        if not self.microphone or not self.recognizer:
            return ""
        
        # Use provided values or defaults from config
        if timeout is None:
            timeout = self.listen_timeout
        if phrase_time_limit is None:
            phrase_time_limit = self.phrase_time_limit
        
        try:
            with self.microphone as source:
                print(f"Listening... (timeout: {timeout}s)")
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

