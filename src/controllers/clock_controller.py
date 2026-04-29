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
    """Abstract base class for all controllers.

    Defines the lifecycle interface that the application uses to start
    and stop each controller's update loop.
    """

    @abstractmethod
    def start(self) -> None:
        """Begin the controller's periodic update loop."""

    @abstractmethod
    def stop(self) -> None:
        """Halt the controller's periodic update loop."""


class ClockController(BaseController):
    """Drives the analog and digital clock views from ClockModel.

    Schedules periodic model updates via the tkinter after() mechanism
    and propagates changes to the registered views.

    Attributes:
        _model: The ClockModel instance.
        _analog_view: The AnalogClockView instance.
        _digital_view: The DigitalClockView instance.
        _timezone_view: The TimezoneView instance.
        _after_fn: Callable wrapping root.after() for scheduling.
        _after_cancel_fn: Callable wrapping root.after_cancel().
        _after_id: Identifier of the pending after() call.
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
        """Initialise ClockController.

        Args:
            model: The ClockModel to drive.
            analog_view: The analog clock canvas view.
            digital_view: The digital time/date view.
            timezone_view: The secondary timezone view.
            after_fn: root.after(delay_ms, callback) callable.
            after_cancel_fn: root.after_cancel(id) callable.
        """
        self._model = model
        self._analog_view = analog_view
        self._digital_view = digital_view
        self._timezone_view = timezone_view
        self._after_fn = after_fn
        self._after_cancel_fn = after_cancel_fn
        self._after_id: Optional[str] = None

        # Subscribe views to model changes
        self._model.subscribe(self._on_model_update)
        logger.debug("ClockController initialised.")

    # ------------------------------------------------------------------
    # BaseController implementation
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin the clock update loop."""
        logger.info("ClockController started.")
        self._tick()

    def stop(self) -> None:
        """Stop the clock update loop."""
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("ClockController stopped.")

    # ------------------------------------------------------------------
    # Timezone management
    # ------------------------------------------------------------------

    def on_timezone_changed(self, tz_name: str) -> None:
        """Handle timezone selection change from the view.

        Args:
            tz_name: The newly selected timezone name string.
        """
        try:
            self._model.set_timezone(tz_name)
        except Exception as exc:
            logger.error("Invalid timezone '%s': %s", tz_name, exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Update the model and schedule the next tick."""
        self._model.update()
        self._after_id = self._after_fn(CLOCK_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        """Push fresh data from the model to all views."""
        hour_angle, minute_angle, second_angle = self._model.get_hand_angles()
        self._analog_view.draw(hour_angle, minute_angle, second_angle)
        self._digital_view.update_time(self._model.format_local_time())
        self._digital_view.update_date(self._model.format_local_date())
        self._digital_view.update_day(self._model.format_local_weekday())
        self._timezone_view.update_time(self._model.format_timezone_time())
