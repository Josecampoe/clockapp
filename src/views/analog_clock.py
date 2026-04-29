"""AnalogClockView: canvas-based analog clock face."""

import logging
import math
import tkinter as tk
from typing import Dict, Tuple

from src.views.main_window import BaseView
from src.utils.constants import (
    CLOCK_CANVAS_SIZE,
    CLOCK_RADIUS,
    CLOCK_CENTER_X,
    CLOCK_CENTER_Y,
    HOUR_HAND_RATIO,
    MINUTE_HAND_RATIO,
    SECOND_HAND_RATIO,
    HOUR_HAND_WIDTH,
    MINUTE_HAND_WIDTH,
    SECOND_HAND_WIDTH,
    CENTER_DOT_RADIUS,
    HOUR_TICK_LENGTH,
    MINUTE_TICK_LENGTH,
    CLOCK_NUMBER_FONT_SIZE,
)

logger = logging.getLogger(__name__)

# Offset so 12 o'clock is at the top (canvas 0° is 3 o'clock)
_ANGLE_OFFSET = -90.0


class AnalogClockView(BaseView):
    """Renders a traditional analog clock face on a tkinter Canvas.

    Attributes:
        _parent: Parent tkinter widget.
        _canvas: The Canvas widget used for drawing.
        _colors: Current theme color dictionary.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise AnalogClockView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._canvas: tk.Canvas = None  # type: ignore[assignment]
        self._colors: Dict[str, str] = {}
        logger.debug("AnalogClockView initialised.")

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create the Canvas widget."""
        self._canvas = tk.Canvas(
            self._parent,
            width=CLOCK_CANVAS_SIZE,
            height=CLOCK_CANVAS_SIZE,
            highlightthickness=0,
        )
        self._canvas.pack(pady=(10, 0))
        self._frame = self._canvas
        logger.debug("AnalogClockView canvas built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Store the new color palette and redraw the static face.

        Args:
            colors: Theme color dictionary.
        """
        self._colors = colors
        self._canvas.configure(bg=colors["bg_window"])

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, hour_angle: float, minute_angle: float, second_angle: float) -> None:
        """Redraw the entire clock face with the given hand angles.

        Args:
            hour_angle: Hour hand angle in degrees from 12 o'clock.
            minute_angle: Minute hand angle in degrees from 12 o'clock.
            second_angle: Second hand angle in degrees from 12 o'clock.
        """
        self._canvas.delete("all")
        self._draw_face()
        self._draw_ticks()
        self._draw_numbers()
        self._draw_hand(hour_angle, HOUR_HAND_RATIO, HOUR_HAND_WIDTH,
                        self._colors.get("hour_hand", "#1A1A1A"))
        self._draw_hand(minute_angle, MINUTE_HAND_RATIO, MINUTE_HAND_WIDTH,
                        self._colors.get("minute_hand", "#333333"))
        self._draw_hand(second_angle, SECOND_HAND_RATIO, SECOND_HAND_WIDTH,
                        self._colors.get("second_hand", "#CC3300"))
        self._draw_center_dot()

    def _draw_face(self) -> None:
        """Draw the circular clock face and border."""
        cx, cy, r = CLOCK_CENTER_X, CLOCK_CENTER_Y, CLOCK_RADIUS
        # Outer shadow / border
        self._canvas.create_oval(
            cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4,
            fill=self._colors.get("clock_border", "#CCCCCC"),
            outline="",
        )
        # Main face
        self._canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=self._colors.get("clock_face", "#FFFFFF"),
            outline=self._colors.get("clock_border", "#CCCCCC"),
            width=2,
        )

    def _draw_ticks(self) -> None:
        """Draw 60 minute ticks and 12 hour ticks around the face."""
        cx, cy, r = CLOCK_CENTER_X, CLOCK_CENTER_Y, CLOCK_RADIUS
        for i in range(60):
            angle_deg = i * 6.0 + _ANGLE_OFFSET
            angle_rad = math.radians(angle_deg)
            is_hour = (i % 5 == 0)
            tick_len = HOUR_TICK_LENGTH if is_hour else MINUTE_TICK_LENGTH
            color = (
                self._colors.get("tick_major", "#222222")
                if is_hour
                else self._colors.get("tick_minor", "#888888")
            )
            width = 2 if is_hour else 1
            outer_x = cx + r * math.cos(angle_rad)
            outer_y = cy + r * math.sin(angle_rad)
            inner_x = cx + (r - tick_len) * math.cos(angle_rad)
            inner_y = cy + (r - tick_len) * math.sin(angle_rad)
            self._canvas.create_line(
                outer_x, outer_y, inner_x, inner_y,
                fill=color, width=width,
            )

    def _draw_numbers(self) -> None:
        """Draw the 1–12 hour numerals around the clock face."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        number_radius = CLOCK_RADIUS - HOUR_TICK_LENGTH - 14
        color = self._colors.get("number_color", "#111111")
        font = ("Helvetica", CLOCK_NUMBER_FONT_SIZE, "bold")
        for hour in range(1, 13):
            angle_deg = hour * 30.0 + _ANGLE_OFFSET
            angle_rad = math.radians(angle_deg)
            x = cx + number_radius * math.cos(angle_rad)
            y = cy + number_radius * math.sin(angle_rad)
            self._canvas.create_text(x, y, text=str(hour), fill=color, font=font)

    def _draw_hand(
        self,
        angle_deg: float,
        length_ratio: float,
        width: int,
        color: str,
    ) -> None:
        """Draw a single clock hand.

        Args:
            angle_deg: Angle in degrees from 12 o'clock (clockwise).
            length_ratio: Hand length as a fraction of the clock radius.
            width: Line width in pixels.
            color: Hex color string for the hand.
        """
        cx, cy, r = CLOCK_CENTER_X, CLOCK_CENTER_Y, CLOCK_RADIUS
        angle_rad = math.radians(angle_deg + _ANGLE_OFFSET)
        end_x = cx + r * length_ratio * math.cos(angle_rad)
        end_y = cy + r * length_ratio * math.sin(angle_rad)
        self._canvas.create_line(
            cx, cy, end_x, end_y,
            fill=color, width=width, capstyle=tk.ROUND,
        )

    def _draw_center_dot(self) -> None:
        """Draw the center pivot dot over all hands."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        r = CENTER_DOT_RADIUS
        color = self._colors.get("center_dot", "#1A1A1A")
        self._canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=color, outline=color,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _polar_to_cartesian(
        cx: float, cy: float, radius: float, angle_deg: float
    ) -> Tuple[float, float]:
        """Convert polar coordinates to Cartesian.

        Args:
            cx: Center x.
            cy: Center y.
            radius: Distance from center.
            angle_deg: Angle in degrees (0 = right, clockwise).

        Returns:
            (x, y) tuple.
        """
        angle_rad = math.radians(angle_deg)
        return cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)
