from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta


DEFAULT_COOLDOWN = timedelta(minutes=30)
INTENT_COOLDOWNS = {
    "strong_rest_reminder": timedelta(minutes=60),
    "welcome_back": timedelta(minutes=5),
}


class SpeechCooldown:
    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or datetime.now
        self._last_spoken_at: dict[str, datetime] = {}

    def allows(self, speech_intent: str) -> bool:
        last_spoken_at = self._last_spoken_at.get(speech_intent)
        if last_spoken_at is None:
            return True
        return self._clock() - last_spoken_at >= self.duration_for(speech_intent)

    def mark_spoken(self, speech_intent: str) -> None:
        self._last_spoken_at[speech_intent] = self._clock()

    @staticmethod
    def duration_for(speech_intent: str) -> timedelta:
        return INTENT_COOLDOWNS.get(speech_intent, DEFAULT_COOLDOWN)

