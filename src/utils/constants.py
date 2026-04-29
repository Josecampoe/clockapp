"""Application-wide constants for the Clock App."""

# Application metadata
APP_TITLE = "Classic Clock"
APP_VERSION = "1.0.0"
APP_WIDTH = 600
APP_HEIGHT = 820

# Clock canvas dimensions
CLOCK_CANVAS_SIZE = 400
CLOCK_RADIUS = 170
CLOCK_CENTER_X = 200
CLOCK_CENTER_Y = 200

# Hand length ratios (relative to radius)
HOUR_HAND_RATIO = 0.60
MINUTE_HAND_RATIO = 0.85
SECOND_HAND_RATIO = 0.90

# Hand widths (pixels)
HOUR_HAND_WIDTH = 6
MINUTE_HAND_WIDTH = 4
SECOND_HAND_WIDTH = 2

# Center dot radius
CENTER_DOT_RADIUS = 6

# Tick mark lengths
HOUR_TICK_LENGTH = 18
MINUTE_TICK_LENGTH = 8

# Number font size on clock face
CLOCK_NUMBER_FONT_SIZE = 13

# Update intervals (milliseconds)
CLOCK_UPDATE_INTERVAL = 500
STOPWATCH_UPDATE_INTERVAL = 50
TIMER_UPDATE_INTERVAL = 100

# Digital clock font sizes
DIGITAL_TIME_FONT_SIZE = 36
DIGITAL_DATE_FONT_SIZE = 14
DIGITAL_DAY_FONT_SIZE = 13

# Alarm
ALARM_DEFAULT_HOUR = 7
ALARM_DEFAULT_MINUTE = 0
ALARM_SOUND_DURATION_MS = 5000

# Stopwatch
STOPWATCH_MAX_HOURS = 99

# Timer
TIMER_MAX_HOURS = 23
TIMER_MAX_MINUTES = 59
TIMER_MAX_SECONDS = 59

# Timezones
TIMEZONE_LIST = [
    "America/Bogota",
    "America/New_York",
    "Europe/London",
    "Europe/Madrid",
    "Asia/Tokyo",
    "Asia/Dubai",
    "Australia/Sydney",
    "UTC",
]

# Theme names
THEME_LIGHT = "light"
THEME_DARK = "dark"

# Light theme colors
LIGHT_THEME = {
    "bg_window": "#F5F5F0",
    "clock_face": "#FFFFFF",
    "clock_border": "#CCCCCC",
    "hour_hand": "#1A1A1A",
    "minute_hand": "#333333",
    "second_hand": "#CC3300",
    "text_primary": "#111111",
    "text_secondary": "#555555",
    "accent": "#4A4AE8",
    "tick_major": "#222222",
    "tick_minor": "#888888",
    "number_color": "#111111",
    "center_dot": "#1A1A1A",
    "button_bg": "#E0E0E0",
    "button_fg": "#111111",
    "button_active_bg": "#C8C8C8",
    "entry_bg": "#FFFFFF",
    "entry_fg": "#111111",
    "frame_bg": "#EBEBEB",
    "label_bg": "#F5F5F0",
    "separator": "#CCCCCC",
}

# Dark theme colors
DARK_THEME = {
    "bg_window": "#1E1E1E",
    "clock_face": "#2A2A2A",
    "clock_border": "#444444",
    "hour_hand": "#EEEEEE",
    "minute_hand": "#CCCCCC",
    "second_hand": "#FF4422",
    "text_primary": "#F0F0F0",
    "text_secondary": "#AAAAAA",
    "accent": "#7B7BFF",
    "tick_major": "#DDDDDD",
    "tick_minor": "#666666",
    "number_color": "#F0F0F0",
    "center_dot": "#EEEEEE",
    "button_bg": "#3A3A3A",
    "button_fg": "#F0F0F0",
    "button_active_bg": "#505050",
    "entry_bg": "#2E2E2E",
    "entry_fg": "#F0F0F0",
    "frame_bg": "#252525",
    "label_bg": "#1E1E1E",
    "separator": "#444444",
}

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "DEBUG"
