#!/bin/bash
# Bosco Core startup wrapper - suppresses ALSA/Jack warnings

# Suppress JACK audio reservation warnings
export JACK_NO_AUDIO_RESERVATION=1

# Use dummy SDL audio driver  
export SDL_AUDIODRIVER=dummy

# Suppress pygame support prompt
export PYGAME_HIDE_SUPPORT_PROMPT=1

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run with venv Python if available
if [ -d "venv" ]; then
    exec venv/bin/python "$@"
else
    exec python3 "$@"
fi

