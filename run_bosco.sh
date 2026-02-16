#!/bin/bash
# Run Bosco Core with ALSA/PulseAudio/Jack warnings suppressed

# Set environment variables
export SDL_AUDIODRIVER=dummy
export PYGAME_HIDE_SUPPORT_PROMPT=1
export JACK_NO_START_SERVER=1

# Run Python and filter out ALSA/Jack/PulseAudio warnings from stderr
python main.py 2> >(grep -vE "ALSA lib|Jack|pcm_|snd_pcm|JackShm|Cannot connect to server|jack server is not running" >&2)

