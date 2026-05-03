import json
import unittest
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory


class ConfigTests(unittest.TestCase):
    def test_load_config_returns_defaults_when_file_is_missing(self):
        from companion_app.config import load_config

        with TemporaryDirectory() as temp_dir:
            config = load_config(Path(temp_dir) / "config.json")

        self.assertEqual(config["personality"], "gentle")
        self.assertFalse(config["ai_enabled"])
        self.assertEqual(config["ai_provider"], "deepseek")
        self.assertEqual(config["pet_size"], 128)

    def test_load_config_recovers_from_invalid_json(self):
        from companion_app.config import load_config

        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text("{not valid json", encoding="utf-8")

            config = load_config(config_path)

        self.assertEqual(config["personality"], "gentle")
        self.assertFalse(config["ai_enabled"])

    def test_save_config_does_not_persist_api_keys(self):
        from companion_app.config import save_config

        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            save_config(
                {
                    "personality": "quiet",
                    "ai_enabled": True,
                    "deepseek_api_key": "secret",
                },
                config_path,
            )

            saved = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["personality"], "quiet")
        self.assertTrue(saved["ai_enabled"])
        self.assertNotIn("deepseek_api_key", saved)


class BehaviorEngineTests(unittest.TestCase):
    def _snapshot(self, active_seconds, idle_seconds=0, returned=None, bucket="afternoon"):
        from companion_app.activity.session_tracker import ActivitySnapshot

        return ActivitySnapshot(
            idle_seconds=idle_seconds,
            active_seconds=active_seconds,
            returned_from_idle_seconds=returned,
            time_bucket=bucket,
            timestamp=datetime(2026, 5, 2, 15, 0, 0),
        )

    def _event(self, event_type, snapshot):
        from companion_app.core.events import ActivityEvent

        return ActivityEvent(type=event_type, snapshot=snapshot)

    def _state(self):
        from companion_app.core.pet_state import PetState

        return PetState(
            personality="gentle",
            mood="calm",
            current_action="idle_lie",
            last_interaction_at=None,
        )

    def test_active_45_minutes_triggers_gentle_rest_reminder(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine()
        decision = engine.decide(
            self._event("long_active_45m", self._snapshot(active_seconds=45 * 60)),
            self._state(),
        )

        self.assertEqual(decision.action_id, "nudge")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "rest_reminder")
        self.assertGreaterEqual(decision.priority, 50)

    def test_active_90_minutes_uses_stronger_reminder(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine()
        decision = engine.decide(
            self._event("long_active_90m", self._snapshot(active_seconds=90 * 60)),
            self._state(),
        )

        self.assertEqual(decision.action_id, "concerned")
        self.assertTrue(decision.should_speak)
        self.assertEqual(decision.speech_intent, "strong_rest_reminder")

    def test_cooldown_prevents_repeating_same_speech_intent(self):
        from companion_app.core.behavior import BehaviorEngine

        engine = BehaviorEngine()
        event = self._event("long_active_45m", self._snapshot(active_seconds=45 * 60))

        first = engine.decide(event, self._state())
        second = engine.decide(event, self._state())

        self.assertTrue(first.should_speak)
        self.assertFalse(second.should_speak)
        self.assertIsNone(second.speech_intent)


class PrivacyContextTests(unittest.TestCase):
    def test_privacy_context_contains_only_allowed_summary_fields(self):
        from companion_app.activity.session_tracker import ActivitySnapshot
        from companion_app.core.pet_state import PetState
        from companion_app.privacy import build_privacy_context

        snapshot = ActivitySnapshot(
            idle_seconds=0,
            active_seconds=52 * 60,
            returned_from_idle_seconds=18 * 60,
            time_bucket="late_night",
            timestamp=datetime(2026, 5, 2, 23, 30, 0),
        )
        state = PetState(
            personality="gentle",
            mood="concerned",
            current_action="concerned",
            last_interaction_at=None,
        )

        context = build_privacy_context(snapshot, state, action_id="concerned")
        payload = asdict(context)

        self.assertEqual(payload["active_minutes"], 52)
        self.assertEqual(payload["returned_from_idle_minutes"], 18)
        self.assertEqual(payload["time_bucket"], "late_night")
        self.assertEqual(payload["personality"], "gentle")
        self.assertEqual(payload["mood"], "concerned")
        self.assertEqual(payload["action_id"], "concerned")

        forbidden_fields = {
            "app_name",
            "window_title",
            "file_name",
            "file_path",
            "keyboard_input",
            "browser_content",
            "chat_content",
            "screenshot",
        }
        self.assertTrue(forbidden_fields.isdisjoint(payload.keys()))


if __name__ == "__main__":
    unittest.main()
