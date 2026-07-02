# Alarm Clock Application

A feature-rich Python alarm clock application with customizable tones and snooze options.

## Features

- ⏰ Set multiple alarms
- 🔊 Customizable alarm tones (built-in and custom audio files)
- 😴 Snooze functionality (5, 10, 15 minute intervals)
- 🖥️ Modern GUI interface with Tkinter
- 📋 Save/Load alarms to persistent storage
- ⏸️ Pause and stop alarms
- 🔔 Visual and audio notifications

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- pygame (for audio playback)

## Installation

```bash
pip install pygame
```

## Usage

```bash
python main.py
```

## Project Structure

```
.
├── main.py                 # Entry point
├── gui/
│   └── alarm_interface.py  # GUI components
├── core/
│   ├── alarm.py           # Alarm class
│   ├── alarm_manager.py   # Alarm management
│   └── audio.py           # Audio playback
├── tones/
│   └── default_tones.py   # Built-in alarm tones
├── audio_files/           # Custom audio files
└── data/
    └── alarms.json        # Persistent storage
```

## API Reference

### Alarm Class

```python
from core.alarm import Alarm
from datetime import datetime

# Create an alarm
alarm = Alarm(
    name="Morning Alarm",
    time=datetime(2026, 7, 2, 7, 0),
    tone="digital",
    enabled=True
)
```

### Alarm Manager

```python
from core.alarm_manager import AlarmManager

manager = AlarmManager()
manager.add_alarm(alarm)
manager.start()
```

## License

MIT
