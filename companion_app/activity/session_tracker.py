from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from companion_app.activity.windows_idle import get_idle_seconds

try:
    from companion_app.core.events import ActivityEvent
except ModuleNotFoundError:

    @dataclass(frozen=True)
    class ActivityEvent:
        type: str
        snapshot: "ActivitySnapshot"


@dataclass(frozen=True)
class ActivitySnapshot:
    idle_seconds: int
    active_seconds: int
    returned_from_idle_seconds: int | None
    time_bucket: str
    timestamp: datetime


class SessionTracker:
    IDLE_5M_SECONDS = 5 * 60
    IDLE_15M_SECONDS = 15 * 60
    LATE_NIGHT_ACTIVE_SECONDS = 30 * 60
    ACTIVE_THRESHOLDS = (
        (90 * 60, "long_active_90m"),
        (45 * 60, "long_active_45m"),
        (25 * 60, "long_active_25m"),
    )

    def __init__(
        self,
        clock: Callable[[], datetime] | None = None,
        idle_seconds_provider: Callable[[], int] | None = None,
    ) -> None:
        self._clock = clock or datetime.now
        self._idle_seconds_provider = idle_seconds_provider or get_idle_seconds
        self._active_started_at: datetime | None = None
        self._was_idle = False
        self._last_idle_seconds = 0
        self._emitted_idle_5m = False
        self._emitted_idle_15m = False
        self._emitted_active_events: set[str] = set()
        self._emitted_late_night_active = False

    def sample(self) -> ActivityEvent:
        now = self._clock()
        idle_seconds = max(0, int(self._idle_seconds_provider()))
        returned_from_idle_seconds = None

        if idle_seconds >= self.IDLE_5M_SECONDS:
            self._was_idle = True
            self._last_idle_seconds = idle_seconds
            active_seconds = 0
            event_type = self._idle_event_type(idle_seconds)
        else:
            if self._was_idle:
                returned_from_idle_seconds = self._last_idle_seconds
                self._reset_active_period(now)
                self._was_idle = False
                active_seconds = 0
                event_type = "return_from_idle"
            else:
                if self._active_started_at is None:
                    self._active_started_at = now
                active_seconds = int((now - self._active_started_at).total_seconds())
                event_type = self._active_event_type(now, active_seconds)

        snapshot = ActivitySnapshot(
            idle_seconds=idle_seconds,
            active_seconds=active_seconds,
            returned_from_idle_seconds=returned_from_idle_seconds,
            time_bucket=self.time_bucket(now),
            timestamp=now,
        )
        return ActivityEvent(type=event_type, snapshot=snapshot)

    @staticmethod
    def time_bucket(moment: datetime) -> str:
        hour = moment.hour
        if 6 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "afternoon"
        if 18 <= hour < 23:
            return "evening"
        return "late_night"

    def _idle_event_type(self, idle_seconds: int) -> str:
        if idle_seconds >= self.IDLE_15M_SECONDS and not self._emitted_idle_15m:
            self._emitted_idle_15m = True
            self._emitted_idle_5m = True
            return "idle_15m"
        if idle_seconds >= self.IDLE_5M_SECONDS and not self._emitted_idle_5m:
            self._emitted_idle_5m = True
            return "idle_5m"
        return "active_tick"

    def _active_event_type(self, now: datetime, active_seconds: int) -> str:
        if (
            self.time_bucket(now) == "late_night"
            and active_seconds >= self.LATE_NIGHT_ACTIVE_SECONDS
            and not self._emitted_late_night_active
        ):
            self._emitted_late_night_active = True
            return "late_night_active"

        for threshold_seconds, event_type in self.ACTIVE_THRESHOLDS:
            if active_seconds >= threshold_seconds and event_type not in self._emitted_active_events:
                self._emitted_active_events.add(event_type)
                return event_type

        return "active_tick"

    def _reset_active_period(self, now: datetime) -> None:
        self._active_started_at = now
        self._emitted_active_events.clear()
        self._emitted_late_night_active = False
        self._emitted_idle_5m = False
        self._emitted_idle_15m = False
