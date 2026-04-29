# Classic Clock

A traditional desktop analog and digital clock application built with Python and tkinter.

## Features

- **Analog Clock** — Classic round face with hour/minute/second hands, tick marks, and numerals 1–12
- **Digital Clock** — Current time (HH:MM:SS), date, and day of the week
- **Alarm** — Set an alarm by hour and minute; audio alert via pygame; enable/disable toggle
- **Stopwatch** — Start, Stop, Reset with HH:MM:SS:ms display
- **Countdown Timer** — Set H/M/S duration; Start, Pause, Reset; audio + visual alert on completion
- **World Clock** — Secondary digital display for 8 selectable timezones
- **Light / Dark Mode** — Toggle button; all widgets update instantly

## Requirements

- Python 3.10+
- pygame 2.5.2
- pytz 2024.1

## Setup

### 1. Install Python

Download and install Python 3.10+ from https://www.python.org/downloads/

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the alarm sound (first time only)

```bash
python generate_alarm_sound.py
```

This creates `assets/alarm_sound.wav`. Skip this step if the file already exists.

### 4. Run the application

```bash
python main.py
```

## Project Structure

```
clock_app/
├── main.py                   # Entry point
├── requirements.txt
├── README.md
├── generate_alarm_sound.py   # One-time WAV generator
├── assets/
│   └── alarm_sound.wav
├── src/
│   ├── app.py                # Main application controller
│   ├── models/
│   │   ├── clock.py          # ClockModel + BaseModel
│   │   ├── alarm.py          # AlarmModel
│   │   ├── stopwatch.py      # StopwatchModel
│   │   └── timer.py          # TimerModel
│   ├── views/
│   │   ├── main_window.py    # MainWindow + BaseView
│   │   ├── analog_clock.py   # Canvas-based analog face
│   │   ├── digital_clock.py  # Digital time/date display
│   │   ├── alarm_view.py     # Alarm UI panel
│   │   ├── stopwatch_view.py # Stopwatch UI panel
│   │   ├── timer_view.py     # Timer UI panel
│   │   └── timezone_view.py  # World clock panel
│   ├── controllers/
│   │   ├── clock_controller.py
│   │   ├── alarm_controller.py
│   │   ├── stopwatch_controller.py
│   │   └── timer_controller.py
│   └── utils/
│       ├── theme.py          # ThemeManager (light/dark)
│       ├── audio.py          # AudioService (pygame wrapper)
│       └── constants.py      # App-wide constants
└── tests/
    ├── test_clock.py
    ├── test_alarm.py
    ├── test_stopwatch.py
    └── test_timer.py
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Architecture

The application follows strict **MVC** (Model-View-Controller):

- **Models** (`src/models/`) — pure business logic, no tkinter imports. All extend `BaseModel(ABC)` and implement the Observer pattern.
- **Views** (`src/views/`) — UI only, no business logic. All extend `BaseView(ABC)`.
- **Controllers** (`src/controllers/`) — mediate between models and views via dependency injection. All extend `BaseController(ABC)`.
- **ThemeManager** — implements Observer pattern; views subscribe and receive color dictionaries on theme change.
- **AudioService** — wraps pygame mixer; degrades gracefully if pygame is unavailable.

## Timezones

The world clock supports:
- America/Bogota
- America/New_York
- Europe/London
- Europe/Madrid
- Asia/Tokyo
- Asia/Dubai
- Australia/Sydney
- UTC
