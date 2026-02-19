#!/usr/bin/env python3
"""
Bosco Core - Clean Audio Runner
This script runs bosco while suppressing ALSA and JACK warnings.
"""

import os
import sys
import subprocess

# Set environment variables BEFORE any audio library imports
# These suppress ALSA, JACK, and PulseAudio warnings

# SDL audio driver (used by some libraries)
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# JACK Audio Connection Kit - suppress all warnings
os.environ['JACK_NO_AUDIO_RESERVATION'] = '1'
os.environ['JACK_NO_START_SERVER'] = '1'
os.environ['JACK_SERVER_NAME'] = 'none'

# PulseAudio - suppress startup warnings
os.environ['PULSE_PROP'] = 'application.name=Bosco'
os.environ['PA_ALSA_PATHS'] = '/dev/null'
os.environ['PA_ALSA_PATHS_FORCE'] = 'yes'

# ALSA configuration - use our custom config
config_dir = os.path.dirname(os.path.abspath(__file__))
asoundrc_path = os.path.join(config_dir, 'asound.conf')
os.environ['ALSA_CONFIG_PATH'] = asoundrc_path

# Suppress pygame prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Also set user-level ALSA config if not already set
home = os.path.expanduser('~')
user_asoundrc = os.path.join(home, '.asoundrc')
if not os.path.exists(user_asoundrc):
    try:
        # Create symlink to our config for user-level
        if os.path.exists(asoundrc_path):
            os.symlink(asoundrc_path, user_asoundrc)
    except:
        pass  # Non-critical if this fails


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

