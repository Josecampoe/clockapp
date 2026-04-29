"""Unit tests for TimerModel."""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.timer import TimerModel


class TestTimerModelSetDuration(unittest.TestCase):
    """Tests for TimerModel.set_duration() validation."""

    def test_set_valid_duration(self):
        model = TimerModel()
        model.set_duration(0, 5, 0)
        self.assertAlmostEqual(model.total_seconds, 300.0, places=3)

    def test_set_duration_zero_raises(self):
        model = TimerModel()
        with self.assertRaises(ValueError):
            model.set_duration(0, 0, 0)

    def test_set_invalid_hours_raises(self):
        model = TimerModel()
        with self.assertRaises(ValueError):
            model.set_duration(24, 0, 0)

    def test_set_invalid_minutes_raises(self):
        model = TimerModel()
        with self.assertRaises(ValueError):
            model.set_duration(0, 60, 0)

    def test_set_invalid_seconds_raises(self):
        model = TimerModel()
        with self.assertRaises(ValueError):
            model.set_duration(0, 0, 60)


class TestTimerModelCountdown(unittest.TestCase):
    """Tests for TimerModel countdown behaviour."""

    def test_initial_state(self):
        model = TimerModel()
        self.assertFalse(model.running)
        self.assertFalse(model.finished)

    def test_start_sets_running(self):
        model = TimerModel()
        model.set_duration(0, 1, 0)
        model.start()
        self.assertTrue(model.running)
        model.pause()

    def test_pause_stops_running(self):
        model = TimerModel()
        model.set_duration(0, 1, 0)
        model.start()
        model.pause()
        self.assertFalse(model.running)

    def test_remaining_decreases_while_running(self):
        model = TimerModel()
        model.set_duration(0, 0, 5)
        model.start()
        time.sleep(0.15)
        remaining = model.remaining_seconds
        model.pause()
        self.assertLess(remaining, 5.0)

    def test_reset_restores_full_duration(self):
        model = TimerModel()
        model.set_duration(0, 0, 10)
        model.start()
        time.sleep(0.1)
        model.pause()
        model.reset()
        self.assertAlmostEqual(model.remaining_seconds, 10.0, places=1)
        self.assertFalse(model.running)
        self.assertFalse(model.finished)

    def test_timer_finishes_when_countdown_reaches_zero(self):
        model = TimerModel()
        model.set_duration(0, 0, 1)
        model.start()
        # Poll until finished or timeout
        deadline = time.monotonic() + 3.0
        while not model.finished and time.monotonic() < deadline:
            model.update()
            time.sleep(0.05)
        self.assertTrue(model.finished)

    def test_acknowledge_clears_finished(self):
        model = TimerModel()
        model.set_duration(0, 0, 1)
        model.start()
        deadline = time.monotonic() + 3.0
        while not model.finished and time.monotonic() < deadline:
            model.update()
            time.sleep(0.05)
        model.acknowledge()
        self.assertFalse(model.finished)


class TestTimerModelFormat(unittest.TestCase):
    """Tests for TimerModel.format_remaining()."""

    def test_format_five_minutes(self):
        model = TimerModel()
        model.set_duration(0, 5, 0)
        self.assertEqual(model.format_remaining(), "00:05:00")

    def test_format_one_hour(self):
        model = TimerModel()
        model.set_duration(1, 0, 0)
        self.assertEqual(model.format_remaining(), "01:00:00")

    def test_format_structure(self):
        model = TimerModel()
        model.set_duration(0, 1, 30)
        result = model.format_remaining()
        parts = result.split(":")
        self.assertEqual(len(parts), 3)


if __name__ == "__main__":
    unittest.main()
