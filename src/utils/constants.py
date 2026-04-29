"""Application-wide constants for the Clock App."""

# Application metadata
APP_TITLE = "Classic Clock"
APP_VERSION = "1.0.0"
APP_WIDTH  = 520
APP_HEIGHT = 720

# Clock canvas dimensions  (square Santos face)
CLOCK_CANVAS_SIZE = 320
CLOCK_RADIUS      = 0       # unused for square; kept for compatibility
CLOCK_CENTER_X    = 160
CLOCK_CENTER_Y    = 160

# Square face geometry
CLOCK_FACE_SIZE   = 240     # outer bezel side length
CLOCK_FACE_INNER  = 210     # dial (white/dark face) side length
CLOCK_FACE_RADIUS = 18      # corner radius of the square face
CLOCK_SCREW_R     = 7       # radius of the corner screws

# Hand length — fraction of half the dial side (105 px)
HOUR_HAND_RATIO   = 0.58
MINUTE_HAND_RATIO = 0.82
SECOND_HAND_RATIO = 0.90

# Hand widths (pixels)
HOUR_HAND_WIDTH   = 7
MINUTE_HAND_WIDTH = 5
SECOND_HAND_WIDTH = 2

# Center dot radius
CENTER_DOT_RADIUS = 7

# Tick mark lengths
HOUR_TICK_LENGTH   = 14
MINUTE_TICK_LENGTH = 6

# Roman numeral font size
CLOCK_NUMBER_FONT_SIZE = 11

# Update intervals (milliseconds)
CLOCK_UPDATE_INTERVAL     = 500
STOPWATCH_UPDATE_INTERVAL = 50
TIMER_UPDATE_INTERVAL     = 100

# Digital clock font sizes
DIGITAL_TIME_FONT_SIZE = 34
DIGITAL_DATE_FONT_SIZE = 13
DIGITAL_DAY_FONT_SIZE  = 12

# Alarm
ALARM_DEFAULT_HOUR     = 7
ALARM_DEFAULT_MINUTE   = 0
ALARM_SOUND_DURATION_MS = 5000

# Stopwatch / Timer limits
STOPWATCH_MAX_HOURS = 99
TIMER_MAX_HOURS     = 23
TIMER_MAX_MINUTES   = 59
TIMER_MAX_SECONDS   = 59

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
THEME_DARK  = "dark"

# ── Palettes ──────────────────────────────────────────────────────────
LIGHT_THEME = {
    "bg_window":      "#F0F2F5",
    "bg_card":        "#FFFFFF",
    "clock_face":     "#FAFAF8",       # warm white dial
    "clock_border":   "#C8A96E",       # gold bezel
    "clock_bezel2":   "#E8C97E",       # lighter gold highlight
    "clock_bezel3":   "#A07840",       # darker gold shadow
    "clock_shadow":   "#B0A898",
    "clock_screw":    "#D4AF70",       # screw head gold
    "clock_screw_hl": "#F0D090",       # screw highlight
    "hour_hand":      "#1C1C2E",
    "minute_hand":    "#1C1C2E",
    "second_hand":    "#C8102E",       # Cartier red
    "text_primary":   "#1C1C2E",
    "text_secondary": "#6B7280",
    "accent":         "#6C63FF",
    "accent2":        "#48CAE4",
    "tick_major":     "#1C1C2E",
    "tick_minor":     "#9CA3AF",
    "number_color":   "#1C1C2E",
    "center_dot":     "#C8102E",
    "button_bg":      "#6C63FF",
    "button_fg":      "#FFFFFF",
    "button_hover":   "#5A52D5",
    "button2_bg":     "#F3F4F6",
    "button2_fg":     "#1C1C2E",
    "entry_bg":       "#F9FAFB",
    "entry_fg":       "#1C1C2E",
    "entry_border":   "#D1D5DB",
    "frame_bg":       "#FFFFFF",
    "nav_bg":         "#FFFFFF",
    "nav_border":     "#E5E7EB",
    "separator":      "#E5E7EB",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
}

DARK_THEME = {
    "bg_window":      "#0F0F1A",
    "bg_card":        "#1A1A2E",
    "clock_face":     "#16213E",       # deep navy dial
    "clock_border":   "#8A8A9A",       # steel/silver bezel
    "clock_bezel2":   "#B0B0C4",       # lighter silver highlight
    "clock_bezel3":   "#505060",       # darker silver shadow
    "clock_shadow":   "#0A0A14",
    "clock_screw":    "#909098",       # screw head silver
    "clock_screw_hl": "#C8C8D8",       # screw highlight
    "hour_hand":      "#E8E8F0",
    "minute_hand":    "#C8C8D8",
    "second_hand":    "#F72585",
    "text_primary":   "#F1F5F9",
    "text_secondary": "#94A3B8",
    "accent":         "#7C3AED",
    "accent2":        "#06B6D4",
    "tick_major":     "#D0D0E0",
    "tick_minor":     "#475569",
    "number_color":   "#D8D8E8",
    "center_dot":     "#F72585",
    "button_bg":      "#7C3AED",
    "button_fg":      "#FFFFFF",
    "button_hover":   "#6D28D9",
    "button2_bg":     "#1E293B",
    "button2_fg":     "#F1F5F9",
    "entry_bg":       "#1E293B",
    "entry_fg":       "#F1F5F9",
    "entry_border":   "#334155",
    "frame_bg":       "#1A1A2E",
    "nav_bg":         "#0F0F1A",
    "nav_border":     "#1E293B",
    "separator":      "#1E293B",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
}

# Logging
LOG_FORMAT      = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL       = "DEBUG"
