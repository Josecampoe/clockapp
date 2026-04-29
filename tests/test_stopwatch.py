"""Unit tests for StopwatchModel."""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.stopwatch import StopwatchModel


class TestStopwatchModelBasic(unittest.TestCase):
    """Tests for basic StopwatchModel state transitions."""

    def test_initial_state(self):
        model = StopwatchModel()
        self.assertFalse(model.running)
        self.assertAlmostEqual(model.elapsed_seconds, 0.0, places=3)

    def test_start_sets_running(self):
        model = StopwatchModel()
        model.start()
        self.assertTrue(model.running)
        model.stop()

    def test_stop_clears_running(self):
        model = StopwatchModel()
        model.start()
        model.stop()
        self.assertFalse(model.running)

    def test_reset_zeroes_elapsed(self):
        model = StopwatchModel()
        model.start()
        time.sleep(0.05)
        model.stop()
        model.reset()
        self.assertAlmostEqual(model.elapsed_seconds, 0.0, places=3)
        self.assertFalse(model.running)

    def test_double_start_is_idempotent(self):
        model = StopwatchModel()
        model.start()
        start_time = model._start_time  # pylint: disable=protected-access
        model.start()  # second call should be a no-op
        self.assertEqual(model._start_time, start_time)  # pylint: disable=protected-access
        model.stop()


class TestStopwatchModelElapsed(unittest.TestCase):
    """Tests for elapsed time accuracy."""

    def test_elapsed_increases_while_running(self):
        model = StopwatchModel()
        model.start()
        time.sleep(0.1)
        elapsed = model.elapsed_seconds
        model.stop()
        self.assertGreater(elapsed, 0.05)

    def test_elapsed_does_not_increase_when_stopped(self):
        model = StopwatchModel()
        model.start()
        time.sleep(0.05)
        model.stop()
        e1 = model.elapsed_seconds
        time.sleep(0.05)
        e2 = model.elapsed_seconds
        self.assertAlmostEqual(e1, e2, places=5)

    def test_elapsed_accumulates_across_start_stop(self):
        model = StopwatchModel()
        model.start()
        time.sleep(0.05)
        model.stop()
        e1 = model.elapsed_seconds
        model.start()
        time.sleep(0.05)
        model.stop()
        e2 = model.elapsed_seconds
        self.assertGreater(e2, e1)


class TestStopwatchModelFormat(unittest.TestCase):
    """Tests for StopwatchModel.format_elapsed()."""

    def test_format_zero(self):
        model = StopwatchModel()
        self.assertEqual(model.format_elapsed(), "00:00:00:00")

    def test_format_structure(self):
        model = StopwatchModel()
        result = model.format_elapsed()
        parts = result.split(":")
        self.assertEqual(len(parts), 4)
        for part in parts:
            self.assertTrue(part.isdigit(), f"Non-digit part: {part}")


if __name__ == "__main__":
    unittest.main()
