"""
Audio Suppression Module
Provides functions to suppress ALSA and JACK warnings in a clean way
"""

import os
import sys
import warnings
import logging
import subprocess

# Suppress ALSA and JACK warnings by redirecting stderr
def suppress_audio_warnings():
    """Set environment variables to suppress audio warnings"""
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    os.environ.setdefault('JACK_NO_AUDIO_RESERVATION', '1')
    os.environ.setdefault('JACK_NO_START_SERVER', '1')
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    
    # Suppress Python warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    
    # Suppress ALSA logging
    try:
        # Try to set ALSA conf path to suppress errors
        os.environ['ALSA_CONF_PATH'] = '/dev/null'
    except:
        pass

def is_audio_available():
    """Check if audio system is available"""
    try:
        # Check PulseAudio
        result = subprocess.run(
            ['pactl', 'info'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def get_audio_devices():
    """Get list of available audio devices"""
    devices = {'input': [], 'output': []}
    
    try:
        # List capture devices
        result = subprocess.run(
            ['arecord', '-l'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'card' in line:
                    devices['input'].append(line.strip())
    except:
        pass
    
    try:
        # List playback devices
        result = subprocess.run(
            ['aplay', '-l'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'card' in line:
                    devices['output'].append(line.strip())
    except:
        pass
    
    return devices

if __name__ == "__main__":
    suppress_audio_warnings()
    print("Audio system check:")
    print(f"  Audio available: {is_audio_available()}")
    devices = get_audio_devices()
    print(f"  Input devices: {len(devices['input'])}")
    print(f"  Output devices: {len(devices['output'])}")

