import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class ActivitySnapshotTests(unittest.TestCase):
    def test_time_bucket_boundaries(self):
        from companion_app.activity.session_tracker import SessionTracker

        cases = [
            (datetime(2026, 5, 2, 6, 0), "morning"),
            (datetime(2026, 5, 2, 11, 59), "morning"),
            (datetime(2026, 5, 2, 12, 0), "afternoon"),
            (datetime(2026, 5, 2, 17, 59), "afternoon"),
            (datetime(2026, 5, 2, 18, 0), "evening"),
            (datetime(2026, 5, 2, 22, 59), "evening"),
            (datetime(2026, 5, 2, 23, 0), "late_night"),
            (datetime(2026, 5, 2, 5, 59), "late_night"),
        ]

        for moment, expected_bucket in cases:
            tracker = SessionTracker(clock=lambda moment=moment: moment, idle_seconds_provider=lambda: 0)
            event = tracker.sample()

            self.assertEqual(event.snapshot.time_bucket, expected_bucket)


class SessionTrackerTests(unittest.TestCase):
    def test_active_seconds_increase_without_real_waiting(self):
        from companion_app.activity.session_tracker import SessionTracker

        start = datetime(2026, 5, 2, 15, 0)
        times = iter([start, start + timedelta(seconds=90)])
        tracker = SessionTracker(clock=lambda: next(times), idle_seconds_provider=lambda: 0)

        first = tracker.sample()
        second = tracker.sample()

        self.assertEqual(first.type, "active_tick")
        self.assertEqual(first.snapshot.active_seconds, 0)
        self.assertEqual(second.type, "active_tick")
        self.assertEqual(second.snapshot.active_seconds, 90)

    def test_idle_threshold_events_are_emitted_once(self):
        from companion_app.activity.session_tracker import SessionTracker

        start = datetime(2026, 5, 2, 15, 0)
        idles = iter([0, 5 * 60, 6 * 60, 15 * 60])
        times = iter([start + timedelta(minutes=offset) for offset in [0, 5, 6, 15]])
        tracker = SessionTracker(clock=lambda: next(times), idle_seconds_provider=lambda: next(idles))

        self.assertEqual(tracker.sample().type, "active_tick")
        self.assertEqual(tracker.sample().type, "idle_5m")
        self.assertEqual(tracker.sample().type, "active_tick")
        self.assertEqual(tracker.sample().type, "idle_15m")

    def test_return_from_idle_includes_idle_duration(self):
        from companion_app.activity.session_tracker import SessionTracker

        start = datetime(2026, 5, 2, 15, 0)
        idles = iter([0, 12 * 60, 0])
        times = iter([start, start + timedelta(minutes=12), start + timedelta(minutes=13)])
        tracker = SessionTracker(clock=lambda: next(times), idle_seconds_provider=lambda: next(idles))

        tracker.sample()
        tracker.sample()
        event = tracker.sample()

        self.assertEqual(event.type, "return_from_idle")
        self.assertEqual(event.snapshot.returned_from_idle_seconds, 12 * 60)
        self.assertEqual(event.snapshot.active_seconds, 0)

    def test_long_active_threshold_events(self):
        from companion_app.activity.session_tracker import SessionTracker

        start = datetime(2026, 5, 2, 15, 0)
        times = iter(
            [
                start,
                start + timedelta(minutes=25),
                start + timedelta(minutes=45),
                start + timedelta(minutes=90),
            ]
        )
        tracker = SessionTracker(clock=lambda: next(times), idle_seconds_provider=lambda: 0)

        tracker.sample()
        self.assertEqual(tracker.sample().type, "long_active_25m")
        self.assertEqual(tracker.sample().type, "long_active_45m")
        self.assertEqual(tracker.sample().type, "long_active_90m")

    def test_late_night_active_event(self):
        from companion_app.activity.session_tracker import SessionTracker

        start = datetime(2026, 5, 2, 23, 0)
        times = iter([start, start + timedelta(minutes=30)])
        tracker = SessionTracker(clock=lambda: next(times), idle_seconds_provider=lambda: 0)

        tracker.sample()
        event = tracker.sample()

        self.assertEqual(event.type, "late_night_active")
        self.assertEqual(event.snapshot.time_bucket, "late_night")


class WindowsIdleTests(unittest.TestCase):
    def test_non_windows_returns_zero(self):
        from companion_app.activity.windows_idle import get_idle_seconds

        with patch("companion_app.activity.windows_idle.sys.platform", "linux"):
            self.assertEqual(get_idle_seconds(), 0)

    def test_ctypes_failure_returns_zero(self):
        from companion_app.activity.windows_idle import get_idle_seconds

        with patch("companion_app.activity.windows_idle.sys.platform", "win32"):
            with patch("companion_app.activity.windows_idle.ctypes.windll", new=Mock()) as windll:
                windll.user32.GetLastInputInfo.side_effect = OSError("ctypes failure")

                self.assertEqual(get_idle_seconds(), 0)


if __name__ == "__main__":
    unittest.main()
