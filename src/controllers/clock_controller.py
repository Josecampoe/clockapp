"""ClockController: mediates between ClockModel and clock views."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.models.clock import ClockModel
from src.views.analog_clock import AnalogClockView
from src.views.digital_clock import DigitalClockView
from src.views.timezone_view import TimezoneView
from src.utils.constants import CLOCK_UPDATE_INTERVAL

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """Abstract base class for all controllers."""

    @abstractmethod
    def start(self) -> None:
        """Begin the controller's periodic update loop."""

    @abstractmethod
    def stop(self) -> None:
        """Halt the controller's periodic update loop."""


class ClockController(BaseController):
    """Drives the analog and digital clock views from ClockModel.

    Hand-drag protocol
    ------------------
    The view calls on_hand_drag(hand, absolute_angle) on every mouse-move.
    The controller translates the absolute angle into a model call that
    sets the appropriate time component.  The auto-tick is paused while
    dragging and resumes on mouse release.

    Attributes:
        _dragging: True while the user holds a hand.
        _after_id: Pending tkinter after() identifier.
    """

    def __init__(
        self,
        model: ClockModel,
        analog_view: AnalogClockView,
        digital_view: DigitalClockView,
        timezone_view: TimezoneView,
        after_fn,
        after_cancel_fn,
    ) -> None:
        self._model           = model
        self._analog_view     = analog_view
        self._digital_view    = digital_view
        self._timezone_view   = timezone_view
        self._after_fn        = after_fn
        self._after_cancel_fn = after_cancel_fn
        self._after_id: Optional[str] = None
        self._dragging: bool  = False

        self._model.subscribe(self._on_model_update)
        self._analog_view.set_on_hand_drag(self._on_hand_drag)
        self._analog_view.set_on_drag_end(self._on_drag_end)

        logger.debug("ClockController initialised.")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("ClockController started.")
        self._tick()

    def stop(self) -> None:
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("ClockController stopped.")

    # ------------------------------------------------------------------
    # Timezone
    # ------------------------------------------------------------------

    def on_timezone_changed(self, tz_name: str) -> None:
        try:
            self._model.set_timezone(tz_name)
        except Exception as exc:
            logger.error("Invalid timezone '%s': %s", tz_name, exc)

    # ------------------------------------------------------------------
    # Drag callbacks (called by AnalogClockView)
    # ------------------------------------------------------------------

    def _on_hand_drag(self, hand: str, absolute_angle: float) -> None:
        """Translate the cursor angle into a model time adjustment.

        Args:
            hand:           'hour', 'minute', or 'second'.
            absolute_angle: Cursor angle in degrees from 12-o'clock [0, 360).
        """
        # Pause auto-tick on first drag event
        if not self._dragging:
            self._dragging = True
            if self._after_id is not None:
                self._after_cancel_fn(self._after_id)
                self._after_id = None

        dispatch = {
            "hour":   self._model.set_time_from_hour_angle,
            "minute": self._model.set_time_from_minute_angle,
            "second": self._model.set_time_from_second_angle,
        }
        handler = dispatch.get(hand)
        if handler:
            handler(absolute_angle)

    def _on_drag_end(self) -> None:
        """Resume the auto-tick after the user releases the mouse."""
        self._dragging = False
        logger.debug("Drag ended — resuming tick.")
        self._tick()

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        if not self._dragging:
            self._model.update()
            self._after_id = self._after_fn(CLOCK_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        """Push fresh model data to all views."""
        h, m, s = self._model.get_hand_angles()
        self._analog_view.draw(h, m, s)
        self._digital_view.update_time(self._model.format_local_time())
        self._digital_view.update_date(self._model.format_local_date())
        self._digital_view.update_day(self._model.format_local_weekday())
        self._timezone_view.update_time(self._model.format_timezone_time())
