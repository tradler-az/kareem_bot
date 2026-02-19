#!/usr/bin/env python3
"""
Bosco Core - Clean Audio Runner
This script runs bosco while suppressing ALSA and JACK warnings.
"""

import os
import sys
import subprocess

# Set environment variables before anything else
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['JACK_NO_AUDIO_RESERVATION'] = '1'
os.environ['JACK_NO_START_SERVER'] = '1'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def main():
    """Run bosco with suppressed warnings"""
    
    # Get the path to bosco.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bosco.py')
    
    # Run with stderr suppressed (send to /dev/null for known warnings)
    # We use a subprocess to isolate the audio libraries
    result = subprocess.run(
        [sys.executable, script_path] + sys.argv[1:],
        env=os.environ.copy(),
        stderr=subprocess.DEVNULL,  # Suppress all stderr
        stdout=sys.stdout,
        stdin=sys.stdin
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

