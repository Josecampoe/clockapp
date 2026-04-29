"""AnalogClockView: square Cartier Santos-style clock with drag-to-adjust hands."""

import logging
import math
import tkinter as tk
from typing import Callable, Dict, Optional, Tuple

import customtkinter as ctk

from src.views.main_window import BaseView
from src.utils.constants import (
    CLOCK_CANVAS_SIZE,
    CLOCK_CENTER_X,
    CLOCK_CENTER_Y,
    CLOCK_FACE_SIZE,
    CLOCK_FACE_INNER,
    CLOCK_FACE_RADIUS,
    CLOCK_SCREW_R,
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

# 12 o'clock is at the top; canvas 0° is 3 o'clock → offset by -90°
_ANGLE_OFFSET = -90.0

# Drag detection
_MIN_DRAG_DIST = 18   # px from center — ignore clicks too close
_LINE_HIT_PX   = 16   # px tolerance along hand body

# Half-side of the inner dial (used as "radius" for hand lengths)
_HALF = CLOCK_FACE_INNER // 2   # 105 px

# Roman numerals for the 12 hour positions
_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV",
    5: "V", 6: "VI", 7: "VII", 8: "VIII",
    9: "IX", 10: "X", 11: "XI", 12: "XII",
}

# Screw positions: (angle_deg from 12 o'clock, distance from center)
# Santos has 8 screws: 4 at corners + 4 at mid-sides of the bezel
_SCREW_ANGLES = [45, 135, 225, 315]          # corner screws
_SCREW_DIST   = (CLOCK_FACE_SIZE // 2) - 2   # just inside the outer bezel edge


class AnalogClockView(BaseView):
    """Square Cartier Santos-style analog clock with draggable hands.

    Visual anatomy
    --------------
    ┌─────────────────────────────┐
    │  Outer shadow (soft)        │
    │  ┌───────────────────────┐  │
    │  │  Bezel (gold/silver)  │  │
    │  │  ● screw  ● screw     │  │
    │  │  ┌─────────────────┐  │  │
    │  │  │   Dial face     │  │  │
    │  │  │  tick marks     │  │  │
    │  │  │  Roman nums     │  │  │
    │  │  │  ── hands ──    │  │  │
    │  │  └─────────────────┘  │  │
    │  │  ● screw  ● screw     │  │
    │  └───────────────────────┘  │
    └─────────────────────────────┘

    Drag interaction
    ----------------
    Click anywhere along a hand body (not just the tip) and drag.
    The controller receives (hand_name, absolute_angle_degrees) on every
    mouse-move and translates it to a time offset in the model.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._canvas: tk.Canvas = None          # type: ignore
        self._colors: Dict[str, str] = {}

        self._hour_angle:   float = 0.0
        self._minute_angle: float = 0.0
        self._second_angle: float = 0.0

        self._dragging_hand: Optional[str] = None
        self._on_hand_drag: Optional[Callable[[str, float], None]] = None
        self._on_drag_end:  Optional[Callable[[], None]] = None

        logger.debug("AnalogClockView initialised.")

    # ── Callback wiring ────────────────────────────────────────────────
    def set_on_hand_drag(self, cb: Callable[[str, float], None]) -> None:
        self._on_hand_drag = cb

    def set_on_drag_end(self, cb: Callable[[], None]) -> None:
        self._on_drag_end = cb

    # ── BaseView ───────────────────────────────────────────────────────
    def build(self) -> None:
        """Create the canvas inside a CTkFrame card."""
        self._card = ctk.CTkFrame(self._parent, corner_radius=8, fg_color="transparent")
        self._card.pack(pady=(10, 4))

        self._canvas = tk.Canvas(
            self._card,
            width=CLOCK_CANVAS_SIZE,
            height=CLOCK_CANVAS_SIZE,
            highlightthickness=0,
            cursor="hand2",
            bd=0,
        )
        self._canvas.pack(padx=6, pady=6)
        self._frame = self._card

        self._canvas.bind("<ButtonPress-1>",   self._on_press)
        self._canvas.bind("<B1-Motion>",       self._on_motion)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)

        logger.debug("AnalogClockView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._colors = colors
        self._card.configure(fg_color=colors["bg_window"])
        self._canvas.configure(bg=colors["bg_window"])

    # ══════════════════════════════════════════════════════════════════
    # Main draw entry point
    # ══════════════════════════════════════════════════════════════════

    def draw(self, hour_angle: float, minute_angle: float, second_angle: float) -> None:
        """Redraw the entire Santos clock face."""
        self._hour_angle   = hour_angle
        self._minute_angle = minute_angle
        self._second_angle = second_angle

        c = self._canvas
        c.delete("all")

        self._draw_outer_shadow()
        self._draw_bezel()
        self._draw_screws()
        self._draw_dial()
        self._draw_ticks()
        self._draw_roman_numerals()
        self._draw_brand_text()
        self._draw_hand(hour_angle,   HOUR_HAND_RATIO,   HOUR_HAND_WIDTH,
                        self._colors.get("hour_hand",   "#1C1C2E"), "hour")
        self._draw_hand(minute_angle, MINUTE_HAND_RATIO, MINUTE_HAND_WIDTH,
                        self._colors.get("minute_hand", "#1C1C2E"), "minute")
        self._draw_second_hand(second_angle)
        self._draw_center_jewel()
        self._draw_hint()

    # ══════════════════════════════════════════════════════════════════
    # Drawing layers
    # ══════════════════════════════════════════════════════════════════

    def _draw_outer_shadow(self) -> None:
        """Soft multi-layer drop shadow beneath the case."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        half   = CLOCK_FACE_SIZE // 2
        r      = CLOCK_FACE_RADIUS
        shadow = self._colors.get("clock_shadow", "#B0A898")

        for offset in (8, 5, 3):
            x0, y0 = cx - half + offset, cy - half + offset
            x1, y1 = cx + half + offset, cy + half + offset
            self._rounded_rect(x0, y0, x1, y1, r + 2, fill=shadow, outline="")

    def _draw_bezel(self) -> None:
        """Three-layer square bezel: shadow edge → main → highlight."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        half   = CLOCK_FACE_SIZE // 2
        r      = CLOCK_FACE_RADIUS

        shadow_col = self._colors.get("clock_bezel3",  "#A07840")
        main_col   = self._colors.get("clock_border",  "#C8A96E")
        hi_col     = self._colors.get("clock_bezel2",  "#E8C97E")

        # Outer shadow edge
        self._rounded_rect(
            cx - half - 1, cy - half - 1,
            cx + half + 1, cy + half + 1,
            r + 1, fill=shadow_col, outline="",
        )
        # Main bezel body
        self._rounded_rect(
            cx - half, cy - half,
            cx + half, cy + half,
            r, fill=main_col, outline="",
        )
        # Inner highlight strip (top-left bevel)
        bw = 4   # bezel width
        self._rounded_rect(
            cx - half + bw, cy - half + bw,
            cx + half - bw, cy + half - bw,
            r - bw, fill=hi_col, outline="",
        )

    def _draw_screws(self) -> None:
        """Draw the 4 corner screws — a Santos signature detail."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        screw_col = self._colors.get("clock_screw",    "#D4AF70")
        hi_col    = self._colors.get("clock_screw_hl", "#F0D090")
        dark_col  = self._colors.get("clock_bezel3",   "#A07840")
        r         = CLOCK_SCREW_R

        for angle_deg in _SCREW_ANGLES:
            a  = math.radians(angle_deg + _ANGLE_OFFSET)
            sx = cx + _SCREW_DIST * math.cos(a)
            sy = cy + _SCREW_DIST * math.sin(a)

            # Screw body
            self._canvas.create_oval(
                sx - r, sy - r, sx + r, sy + r,
                fill=screw_col, outline=dark_col, width=1,
            )
            # Highlight dot (top-left)
            hr = max(1, r // 2)
            self._canvas.create_oval(
                sx - r + 1, sy - r + 1,
                sx - r + 1 + hr, sy - r + 1 + hr,
                fill=hi_col, outline="",
            )
            # Cross slot (horizontal)
            self._canvas.create_line(
                sx - r + 2, sy, sx + r - 2, sy,
                fill=dark_col, width=1,
            )
            # Cross slot (vertical)
            self._canvas.create_line(
                sx, sy - r + 2, sx, sy + r - 2,
                fill=dark_col, width=1,
            )

    def _draw_dial(self) -> None:
        """Draw the inner dial face (the white/dark square)."""
        cx, cy  = CLOCK_CENTER_X, CLOCK_CENTER_Y
        half    = CLOCK_FACE_INNER // 2
        r       = CLOCK_FACE_RADIUS - 4
        face    = self._colors.get("clock_face",   "#FAFAF8")
        outline = self._colors.get("clock_bezel3", "#A07840")

        self._rounded_rect(
            cx - half, cy - half,
            cx + half, cy + half,
            r, fill=face, outline=outline, width=1,
        )

    def _draw_ticks(self) -> None:
        """Draw 60 minute ticks and 12 hour ticks around the dial."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        # Ticks are placed just inside the dial edge
        outer_r = CLOCK_FACE_INNER // 2 - 4

        for i in range(60):
            a      = math.radians(i * 6.0 + _ANGLE_OFFSET)
            is_h   = (i % 5 == 0)
            tl     = HOUR_TICK_LENGTH if is_h else MINUTE_TICK_LENGTH
            color  = self._colors.get("tick_major" if is_h else "tick_minor", "#888")
            width  = 2 if is_h else 1

            ox = cx + outer_r * math.cos(a)
            oy = cy + outer_r * math.sin(a)
            ix = cx + (outer_r - tl) * math.cos(a)
            iy = cy + (outer_r - tl) * math.sin(a)
            self._canvas.create_line(ox, oy, ix, iy, fill=color, width=width, capstyle=tk.ROUND)

    def _draw_roman_numerals(self) -> None:
        """Draw Roman numerals at the 12 hour positions."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        # Place numerals inside the tick marks
        nr    = CLOCK_FACE_INNER // 2 - HOUR_TICK_LENGTH - 12
        col   = self._colors.get("number_color", "#1C1C2E")
        fnt   = ("Georgia", CLOCK_NUMBER_FONT_SIZE, "bold")

        for h in range(1, 13):
            a = math.radians(h * 30.0 + _ANGLE_OFFSET)
            x = cx + nr * math.cos(a)
            y = cy + nr * math.sin(a)
            self._canvas.create_text(x, y, text=_ROMAN[h], fill=col, font=fnt)

    def _draw_brand_text(self) -> None:
        """Draw 'SANTOS' brand text below 12 and 'DE CARTIER' below that."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        col    = self._colors.get("number_color", "#1C1C2E")

        self._canvas.create_text(
            cx, cy - 38,
            text="SANTOS",
            fill=col,
            font=("Georgia", 8, "bold"),
            anchor="center",
        )
        self._canvas.create_text(
            cx, cy - 26,
            text="DE CARTIER",
            fill=col,
            font=("Georgia", 6),
            anchor="center",
        )

    # ── Hands ──────────────────────────────────────────────────────────

    def _draw_hand(self, angle_deg: float, ratio: float, width: int,
                   color: str, tag: str) -> None:
        """Draw a dauphine (leaf-shaped) hand.

        The dauphine shape is approximated with a thick tapered line:
        wide at the base, narrowing to a point at the tip.
        """
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        length = _HALF * ratio
        a      = math.radians(angle_deg + _ANGLE_OFFSET)

        # Tip
        ex = cx + length * math.cos(a)
        ey = cy + length * math.sin(a)
        # Back tail (short counter-weight)
        tail_len = length * 0.14
        bx = cx - tail_len * math.cos(a)
        by = cy - tail_len * math.sin(a)

        if self._dragging_hand == tag:
            color = self._colors.get("accent", "#6C63FF")
            width += 2

        # Shadow
        shadow = self._colors.get("clock_shadow", "#B0A898")
        self._canvas.create_line(
            bx + 1, by + 1, ex + 1, ey + 1,
            fill=shadow, width=width + 2, capstyle=tk.ROUND,
        )
        # Main hand body (thick)
        mid_x = cx + (length * 0.5) * math.cos(a)
        mid_y = cy + (length * 0.5) * math.sin(a)
        self._canvas.create_line(
            bx, by, mid_x, mid_y,
            fill=color, width=width, capstyle=tk.ROUND, tags=(tag,),
        )
        # Tapered tip (thinner)
        self._canvas.create_line(
            mid_x, mid_y, ex, ey,
            fill=color, width=max(1, width - 2), capstyle=tk.ROUND, tags=(tag,),
        )

    def _draw_second_hand(self, angle_deg: float) -> None:
        """Thin needle second hand with a small lollipop counterweight."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        length = _HALF * SECOND_HAND_RATIO
        a      = math.radians(angle_deg + _ANGLE_OFFSET)
        col    = self._colors.get("second_hand", "#C8102E")

        if self._dragging_hand == "second":
            col = self._colors.get("accent", "#6C63FF")

        # Long needle
        ex = cx + length * math.cos(a)
        ey = cy + length * math.sin(a)
        # Counter-tail with lollipop
        tail = length * 0.22
        bx   = cx - tail * math.cos(a)
        by   = cy - tail * math.sin(a)

        # Needle shadow
        shadow = self._colors.get("clock_shadow", "#B0A898")
        self._canvas.create_line(
            bx + 1, by + 1, ex + 1, ey + 1,
            fill=shadow, width=SECOND_HAND_WIDTH + 1, capstyle=tk.ROUND,
        )
        # Needle
        self._canvas.create_line(
            bx, by, ex, ey,
            fill=col, width=SECOND_HAND_WIDTH, capstyle=tk.ROUND, tags=("second",),
        )
        # Lollipop circle at tail
        lr = 5
        self._canvas.create_oval(
            bx - lr, by - lr, bx + lr, by + lr,
            fill=col, outline="",
        )

    def _draw_center_jewel(self) -> None:
        """Draw the center pivot: outer ring + inner dot (Cartier style)."""
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        col    = self._colors.get("center_dot",  "#C8102E")
        face   = self._colors.get("clock_face",  "#FAFAF8")
        bezel  = self._colors.get("clock_border","#C8A96E")

        r_outer = CENTER_DOT_RADIUS + 3
        r_inner = CENTER_DOT_RADIUS - 1

        # Gold/silver ring
        self._canvas.create_oval(
            cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
            fill=bezel, outline="",
        )
        # Colored center
        self._canvas.create_oval(
            cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
            fill=col, outline="",
        )
        # White highlight dot
        self._canvas.create_oval(
            cx - 2, cy - 2, cx + 2, cy + 2,
            fill=face, outline="",
        )

    def _draw_hint(self) -> None:
        """Small drag hint below the case."""
        hint_color = self._colors.get("text_secondary", "#888")
        if self._dragging_hand:
            names = {"hour": "hora", "minute": "minutos", "second": "segundos"}
            msg        = f"Ajustando {names.get(self._dragging_hand, '')}…"
            hint_color = self._colors.get("accent", "#6C63FF")
        else:
            msg = "Arrastra una manecilla para ajustar"

        self._canvas.create_text(
            CLOCK_CENTER_X,
            CLOCK_CENTER_Y + CLOCK_FACE_SIZE // 2 + 14,
            text=msg, fill=hint_color, font=("Helvetica", 8),
        )

    # ══════════════════════════════════════════════════════════════════
    # Geometry helpers
    # ══════════════════════════════════════════════════════════════════

    def _rounded_rect(
        self,
        x0: float, y0: float, x1: float, y1: float,
        radius: float,
        **kwargs,
    ) -> None:
        """Draw a rounded rectangle on the canvas.

        Args:
            x0, y0: Top-left corner.
            x1, y1: Bottom-right corner.
            radius:  Corner radius in pixels.
            **kwargs: Passed directly to ``create_polygon``.
        """
        r = radius
        points = [
            x0 + r, y0,
            x1 - r, y0,
            x1,     y0,
            x1,     y0 + r,
            x1,     y1 - r,
            x1,     y1,
            x1 - r, y1,
            x0 + r, y1,
            x0,     y1,
            x0,     y1 - r,
            x0,     y0 + r,
            x0,     y0,
        ]
        self._canvas.create_polygon(points, smooth=True, **kwargs)

    def _cursor_angle(self, x: float, y: float) -> float:
        """Angle in degrees from 12 o'clock to cursor, clockwise, [0, 360)."""
        dx = x - CLOCK_CENTER_X
        dy = y - CLOCK_CENTER_Y
        return (math.degrees(math.atan2(dy, dx)) - _ANGLE_OFFSET) % 360.0

    def _dist_to_segment(
        self,
        px: float, py: float,
        ax: float, ay: float,
        bx: float, by: float,
    ) -> float:
        """Perpendicular distance from point P to segment AB."""
        dx, dy = bx - ax, by - ay
        seg    = dx * dx + dy * dy
        if seg == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    def _hand_tip(self, angle_deg: float, ratio: float) -> Tuple[float, float]:
        a = math.radians(angle_deg + _ANGLE_OFFSET)
        return (
            CLOCK_CENTER_X + _HALF * ratio * math.cos(a),
            CLOCK_CENTER_Y + _HALF * ratio * math.sin(a),
        )

    def _pick_hand(self, x: float, y: float) -> Optional[str]:
        """Return the name of the hand closest to (x, y) along its body."""
        if math.hypot(x - CLOCK_CENTER_X, y - CLOCK_CENTER_Y) < _MIN_DRAG_DIST:
            return None
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        hands  = [
            ("hour",   self._hour_angle,   HOUR_HAND_RATIO),
            ("minute", self._minute_angle, MINUTE_HAND_RATIO),
            ("second", self._second_angle, SECOND_HAND_RATIO),
        ]
        best, best_d = None, float("inf")
        for name, angle, ratio in hands:
            tx, ty = self._hand_tip(angle, ratio)
            d = self._dist_to_segment(x, y, cx, cy, tx, ty)
            if d < best_d:
                best_d, best = d, name
        return best if best_d <= _LINE_HIT_PX else None

    # ══════════════════════════════════════════════════════════════════
    # Mouse events
    # ══════════════════════════════════════════════════════════════════

    def _on_press(self, event: tk.Event) -> None:
        hand = self._pick_hand(event.x, event.y)
        if hand:
            self._dragging_hand = hand
            logger.debug("Grabbed hand: %s", hand)

    def _on_motion(self, event: tk.Event) -> None:
        if not self._dragging_hand:
            return
        if math.hypot(event.x - CLOCK_CENTER_X, event.y - CLOCK_CENTER_Y) < _MIN_DRAG_DIST:
            return
        angle = self._cursor_angle(event.x, event.y)
        if self._on_hand_drag:
            self._on_hand_drag(self._dragging_hand, angle)

    def _on_release(self, event: tk.Event) -> None:
        if self._dragging_hand:
            logger.debug("Released hand: %s", self._dragging_hand)
            self._dragging_hand = None
            if self._on_drag_end:
                self._on_drag_end()
