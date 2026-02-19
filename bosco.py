#!/usr/bin/env python3
"""
Bosco Core - Silent Startup Wrapper
Suppresses ALSA/PulseAudio/Jack warnings for cleaner output
"""

import os
import sys
import warnings
import subprocess
import threading

def suppress_audio_warnings():
    """Suppress audio library warnings in a separate thread"""
    # Set environment variables before importing audio libs
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    os.environ['JACK_NO_START_SERVER'] = '1'
    os.environ['JACK_NO_AUDIO_RESERVATION'] = '1'  # Prevent Jack from claiming audio devices
    
    # Suppress Python warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=UserWarning)

def main():
    suppress_audio_warnings()
    
    # Import and run main
    import main as bosco_main
    bosco_main.main()

if __name__ == "__main__":
    main()

