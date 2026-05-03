from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from companion_app.core.cooldown import SpeechCooldown
from companion_app.core.events import ActivityEvent
from companion_app.core.pet_state import PetState


@dataclass(frozen=True)
class BehaviorDecision:
    action_id: str
    should_speak: bool
    speech_intent: str | None
    priority: int


@dataclass(frozen=True)
class _RuleDecision:
    action_id: str
    speech_intent: str | None
    priority: int


class BehaviorEngine:
    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._cooldown = SpeechCooldown(clock=clock)

    def decide(self, event: ActivityEvent, pet_state: PetState) -> BehaviorDecision:
        del pet_state
        rule_decision = self._match_rule(event)
        speech_intent = rule_decision.speech_intent
        should_speak = False

        if speech_intent is not None and self._cooldown.allows(speech_intent):
            should_speak = True
            self._cooldown.mark_spoken(speech_intent)

        return BehaviorDecision(
            action_id=rule_decision.action_id,
            should_speak=should_speak,
            speech_intent=speech_intent if should_speak else None,
            priority=rule_decision.priority,
        )

    def _match_rule(self, event: ActivityEvent) -> _RuleDecision:
        snapshot = event.snapshot
        active_seconds = getattr(snapshot, "active_seconds", 0) or 0
        idle_seconds = getattr(snapshot, "idle_seconds", 0) or 0
        returned_seconds = getattr(snapshot, "returned_from_idle_seconds", None)
        time_bucket = getattr(snapshot, "time_bucket", None)

        if event.type == "return_from_idle" or (
            returned_seconds is not None and returned_seconds >= 5 * 60
        ):
            return _RuleDecision("wake_up", "welcome_back", 80)

        if event.type == "late_night_active" or (
            time_bucket == "late_night" and active_seconds >= 30 * 60
        ):
            return _RuleDecision("concerned", "late_night_care", 75)

        if event.type == "long_active_90m" or active_seconds >= 90 * 60:
            return _RuleDecision("concerned", "strong_rest_reminder", 70)

        if event.type == "long_active_45m" or active_seconds >= 45 * 60:
            return _RuleDecision("nudge", "rest_reminder", 50)

        if event.type == "idle_15m" or idle_seconds >= 15 * 60:
            return _RuleDecision("sleep", None, 40)

        if event.type == "idle_5m" or idle_seconds >= 5 * 60:
            return _RuleDecision("sit_wait", None, 30)

        if event.type == "long_active_25m" or active_seconds >= 25 * 60:
            return _RuleDecision("stretch", "soft_checkin", 20)

        return _RuleDecision("idle_lie", None, 10)
