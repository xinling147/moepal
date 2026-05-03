from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest


class BehaviorEngineRuleTests(unittest.TestCase):
    def _snapshot(
        self,
        active_seconds=0,
        idle_seconds=0,
        returned_from_idle_seconds=None,
        time_bucket="afternoon",
    ):
        return SimpleNamespace(
            active_seconds=active_seconds,
            idle_seconds=idle_seconds,
            returned_from_idle_seconds=returned_from_idle_seconds,
            time_bucket=time_bucket,
            timestamp=datetime(2026, 5, 2, 15, 0, 0),
        )

    def _event(self, event_type, snapshot):
        from companion_app.core.events import ActivityEvent

        return ActivityEvent(type=event_type, snapshot=snapshot)

    def _state(self):
        from companion_app.core.pet_state import PetState

        return PetState()

    def test_long_active_25_minutes_stretches_with_soft_checkin(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event(
                "long_active_25m",
                self._snapshot(active_seconds=25 * 60),
            ),
            self._state(),
        )

        self.assertEqual(decision.action_id, "stretch")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "soft_checkin")
        self.assertEqual(decision.priority, 20)

    def test_long_active_45_minutes_nudges_with_rest_reminder(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event(
                "long_active_45m",
                self._snapshot(active_seconds=45 * 60),
            ),
            self._state(),
        )

        self.assertEqual(decision.action_id, "nudge")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "rest_reminder")
        self.assertEqual(decision.priority, 50)

    def test_long_active_90_minutes_uses_strong_rest_reminder(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event(
                "long_active_90m",
                self._snapshot(active_seconds=90 * 60),
            ),
            self._state(),
        )

        self.assertEqual(decision.action_id, "concerned")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "strong_rest_reminder")
        self.assertEqual(decision.priority, 70)

    def test_idle_5_minutes_waits_without_speech(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event("idle_5m", self._snapshot(idle_seconds=5 * 60)),
            self._state(),
        )

        self.assertEqual(decision.action_id, "sit_wait")
        self.assertFalse(decision.should_speak)
        self.assertIsNone(decision.speech_intent)
        self.assertEqual(decision.priority, 30)

    def test_idle_15_minutes_sleeps_without_speech(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event("idle_15m", self._snapshot(idle_seconds=15 * 60)),
            self._state(),
        )

        self.assertEqual(decision.action_id, "sleep")
        self.assertFalse(decision.should_speak)
        self.assertIsNone(decision.speech_intent)
        self.assertEqual(decision.priority, 40)

    def test_return_from_idle_welcomes_back_with_high_priority(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 15, 0, 0))

        decision = engine.decide(
            self._event(
                "return_from_idle",
                self._snapshot(returned_from_idle_seconds=7 * 60),
            ),
            self._state(),
        )

        self.assertEqual(decision.action_id, "wake_up")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "welcome_back")
        self.assertEqual(decision.priority, 80)

    def test_late_night_active_takes_priority_over_regular_active_reminder(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=lambda: datetime(2026, 5, 2, 23, 30, 0))

        decision = engine.decide(
            self._event(
                "late_night_active",
                self._snapshot(
                    active_seconds=45 * 60,
                    time_bucket="late_night",
                ),
            ),
            self._state(),
        )

        self.assertEqual(decision.action_id, "concerned")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "late_night_care")
        self.assertEqual(decision.priority, 75)

    def test_speech_intent_cooldown_uses_injected_clock(self):
        current_time = datetime(2026, 5, 2, 15, 0, 0)

        def clock():
            return current_time

        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=clock)
        event = self._event(
            "long_active_45m",
            self._snapshot(active_seconds=45 * 60),
        )

        first = engine.decide(event, self._state())
        second = engine.decide(event, self._state())
        current_time += timedelta(minutes=31)
        third = engine.decide(event, self._state())

        self.assertTrue(first.should_speak)
        self.assertFalse(second.should_speak)
        self.assertIsNone(second.speech_intent)
        self.assertTrue(third.should_speak)
        self.assertEqual(third.speech_intent, "rest_reminder")

    def test_strong_rest_reminder_has_sixty_minute_cooldown(self):
        current_time = datetime(2026, 5, 2, 15, 0, 0)

        def clock():
            return current_time

        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=clock)
        event = self._event(
            "long_active_90m",
            self._snapshot(active_seconds=90 * 60),
        )

        first = engine.decide(event, self._state())
        current_time += timedelta(minutes=31)
        second = engine.decide(event, self._state())
        current_time += timedelta(minutes=30)
        third = engine.decide(event, self._state())

        self.assertTrue(first.should_speak)
        self.assertFalse(second.should_speak)
        self.assertIsNone(second.speech_intent)
        self.assertTrue(third.should_speak)
        self.assertEqual(third.speech_intent, "strong_rest_reminder")

    def test_welcome_back_has_five_minute_cooldown(self):
        current_time = datetime(2026, 5, 2, 15, 0, 0)

        def clock():
            return current_time

        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine(clock=clock)
        event = self._event(
            "return_from_idle",
            self._snapshot(returned_from_idle_seconds=8 * 60),
        )

        first = engine.decide(event, self._state())
        current_time += timedelta(minutes=4)
        second = engine.decide(event, self._state())
        current_time += timedelta(minutes=2)
        third = engine.decide(event, self._state())

        self.assertTrue(first.should_speak)
        self.assertFalse(second.should_speak)
        self.assertIsNone(second.speech_intent)
        self.assertTrue(third.should_speak)
        self.assertEqual(third.speech_intent, "welcome_back")


if __name__ == "__main__":
    unittest.main()
