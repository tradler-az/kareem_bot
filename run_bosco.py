#!/usr/bin/env python3
"""
Bosco Core - Audio Suppression Wrapper
This wrapper suppresses ALSA and JACK warnings before importing voice modules.
"""

import os
import sys
import io
import tempfile
import logging

# Suppress ALSA and JACK warnings at the C library level
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('JACK_NO_AUDIO_RESERVATION', '1')
os.environ.setdefault('JACK_NO_START_SERVER', '1')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

# Suppress warnings before importing any audio-related modules
def suppress_audio_warnings():
    """Redirect stderr to suppress ALSA/JACK warnings"""
    # Open /dev/null for suppressing output
    devnull = open(os.devnull, 'w')
    
    # Save original stderr
    original_stderr = sys.stderr
    
    # Suppress stderr temporarily
    sys.stderr = devnull
    
    return original_stderr, devnull

# Suppress warnings during imports
_original_stderr, _devnull = suppress_audio_warnings()

# Now import the audio modules - warnings are suppressed
try:
    # Import voice modules
    from voice import listener, speaker
    from voice.audio_helpers import suppress_audio_warnings as ah_suppress
    
    # Restore stderr after imports
    sys.stderr = _original_stderr
    _devnull.close()
    
    print("✓ Voice modules loaded successfully")
    print(f"  - Listener: {'Available' if listener.SPEECH_RECOGNITION_AVAILABLE else 'Not available'}")
    print(f"  - Speaker: {'pyttsx3' if speaker.PYTTSX3_AVAILABLE else 'gTTS' if speaker.GTTS_AVAILABLE else 'None'}")
    
except Exception as e:
    # Restore stderr on error
    sys.stderr = _original_stderr
    _devnull.close()
    
    print(f"Error loading voice modules: {e}")
    sys.exit(1)

def run_main():
    """Run the main bosco application"""
    import bosco
    bosco.main()

if __name__ == "__main__":
    run_main()

