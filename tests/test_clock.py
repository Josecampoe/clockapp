"""Unit tests for ClockModel."""

import sys
import os
import unittest
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.clock import ClockModel


class TestClockModelHandAngles(unittest.TestCase):
    """Tests for ClockModel.get_hand_angles()."""

    def _make_model_at(self, hour: int, minute: int, second: int) -> ClockModel:
        """Return a ClockModel whose local_time is fixed to the given time."""
        model = ClockModel()
        fixed_dt = datetime(2026, 4, 28, hour, minute, second)
        with patch("src.models.clock.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        # Manually set the internal time for angle calculation
        model._local_time = fixed_dt  # pylint: disable=protected-access
        return model

    def test_twelve_oclock(self):
        """All hands should point to 0° at exactly 12:00:00."""
        model = self._make_model_at(0, 0, 0)
        h, m, s = model.get_hand_angles()
        self.assertAlmostEqual(h, 0.0, places=5)
        self.assertAlmostEqual(m, 0.0, places=5)
        self.assertAlmostEqual(s, 0.0, places=5)

    def test_three_oclock(self):
        """Hour hand should be at 90° at 3:00:00."""
        model = self._make_model_at(3, 0, 0)
        h, m, s = model.get_hand_angles()
        self.assertAlmostEqual(h, 90.0, places=4)
        self.assertAlmostEqual(m, 0.0, places=5)
        self.assertAlmostEqual(s, 0.0, places=5)

    def test_six_oclock(self):
        """Hour hand should be at 180° at 6:00:00."""
        model = self._make_model_at(6, 0, 0)
        h, _, _ = model.get_hand_angles()
        self.assertAlmostEqual(h, 180.0, places=4)

    def test_minute_hand_at_30_minutes(self):
        """Minute hand should be at 180° at XX:30:00."""
        model = self._make_model_at(0, 30, 0)
        _, m, _ = model.get_hand_angles()
        self.assertAlmostEqual(m, 180.0, places=4)

    def test_second_hand_at_30_seconds(self):
        """Second hand should be at 180° at XX:XX:30."""
        model = self._make_model_at(0, 0, 30)
        _, _, s = model.get_hand_angles()
        self.assertAlmostEqual(s, 180.0, places=4)

    def test_hour_hand_advances_with_minutes(self):
        """Hour hand at 12:30 should be halfway between 12 and 1 (15°)."""
        model = self._make_model_at(0, 30, 0)
        h, _, _ = model.get_hand_angles()
        self.assertAlmostEqual(h, 15.0, places=4)

    def test_angles_are_non_negative(self):
        """All hand angles must be >= 0."""
        model = self._make_model_at(11, 59, 59)
        h, m, s = model.get_hand_angles()
        self.assertGreaterEqual(h, 0.0)
        self.assertGreaterEqual(m, 0.0)
        self.assertGreaterEqual(s, 0.0)

    def test_angles_less_than_360(self):
        """All hand angles must be < 360."""
        model = self._make_model_at(11, 59, 59)
        h, m, s = model.get_hand_angles()
        self.assertLess(h, 360.0)
        self.assertLess(m, 360.0)
        self.assertLess(s, 360.0)


class TestClockModelFormatters(unittest.TestCase):
    """Tests for ClockModel formatting methods."""

    def setUp(self):
        self.model = ClockModel()
        self.model._local_time = datetime(2026, 4, 28, 14, 5, 9)  # pylint: disable=protected-access

    def test_format_local_time(self):
        self.assertEqual(self.model.format_local_time(), "14:05:09")

    def test_format_local_date(self):
        self.assertEqual(self.model.format_local_date(), "28 April 2026")

    def test_format_local_weekday(self):
        self.assertEqual(self.model.format_local_weekday(), "Tuesday")


class TestClockModelTimezone(unittest.TestCase):
    """Tests for ClockModel timezone handling."""

    def test_set_valid_timezone(self):
        model = ClockModel()
        model.set_timezone("America/Bogota")
        self.assertEqual(str(model.selected_timezone), "America/Bogota")

    def test_set_invalid_timezone_raises(self):
        model = ClockModel()
        import pytz
        with self.assertRaises(pytz.exceptions.UnknownTimeZoneError):
            model.set_timezone("Not/ATimezone")

    def test_get_timezone_names_returns_list(self):
        model = ClockModel()
        names = model.get_timezone_names()
        self.assertIsInstance(names, list)
        self.assertIn("UTC", names)
        self.assertGreaterEqual(len(names), 8)


if __name__ == "__main__":
    unittest.main()
