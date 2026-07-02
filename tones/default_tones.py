"""
Default alarm tone definitions.
"""

import os

# Base directory for audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio_files")

# Available alarm tones mapped to audio file paths
TONES = {
    "digital": os.path.join(AUDIO_DIR, "digital.wav"),
    "classic": os.path.join(AUDIO_DIR, "classic.wav"),
    "gentle": os.path.join(AUDIO_DIR, "gentle.wav"),
    "buzzer": os.path.join(AUDIO_DIR, "buzzer.wav"),
    "chime": os.path.join(AUDIO_DIR, "chime.wav"),
}

# Tone descriptions
TONE_DESCRIPTIONS = {
    "digital": "Sharp digital beep",
    "classic": "Classic alarm clock sound",
    "gentle": "Soft and gradual wake-up tone",
    "buzzer": "Loud buzzer sound",
    "chime": "Pleasant chime notification",
}
