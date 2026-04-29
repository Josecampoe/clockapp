"""StopwatchController: mediates between StopwatchModel and StopwatchView."""

import logging
from typing import Optional

from src.controllers.clock_controller import BaseController
from src.models.stopwatch import StopwatchModel
from src.views.stopwatch_view import StopwatchView
from src.utils.constants import STOPWATCH_UPDATE_INTERVAL

logger = logging.getLogger(__name__)


class StopwatchController(BaseController):
    """Drives the stopwatch feature.

    Attributes:
        _model: The StopwatchModel instance.
        _view: The StopwatchView instance.
        _after_fn: Callable for scheduling.
        _after_cancel_fn: Callable for cancelling scheduled calls.
        _after_id: Identifier of the pending after() call.
    """

    def __init__(
        self,
        model: StopwatchModel,
        view: StopwatchView,
        after_fn,
        after_cancel_fn,
    ) -> None:
        """Initialise StopwatchController.

        Args:
            model: The StopwatchModel to drive.
            view: The StopwatchView to update.
            after_fn: root.after(delay_ms, callback) callable.
            after_cancel_fn: root.after_cancel(id) callable.
        """
        self._model = model
        self._view = view
        self._after_fn = after_fn
        self._after_cancel_fn = after_cancel_fn
        self._after_id: Optional[str] = None

        # Wire view callbacks
        self._view.set_on_start(self._on_start)
        self._view.set_on_stop(self._on_stop)
        self._view.set_on_reset(self._on_reset)

        # Subscribe to model changes
        self._model.subscribe(self._on_model_update)
        logger.debug("StopwatchController initialised.")

    # ------------------------------------------------------------------
    # BaseController implementation
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin the stopwatch display update loop."""
        logger.info("StopwatchController started.")
        self._tick()

    def stop(self) -> None:
        """Stop the display update loop."""
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("StopwatchController stopped.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Refresh the model and schedule the next tick."""
        self._model.update()
        self._after_id = self._after_fn(STOPWATCH_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        """Push elapsed time to the view."""
        self._view.update_elapsed(self._model.format_elapsed())
        self._view.set_running_state(self._model.running)

    # ------------------------------------------------------------------
    # View event handlers
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        """Handle Start button click."""
        self._model.start()

    def _on_stop(self) -> None:
        """Handle Stop button click."""
        self._model.stop()

    def _on_reset(self) -> None:
        """Handle Reset button click."""
        self._model.reset()
        self._view.update_elapsed(self._model.format_elapsed())
        self._view.set_running_state(False)
