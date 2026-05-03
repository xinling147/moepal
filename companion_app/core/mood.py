from __future__ import annotations

from companion_app.core.events import ActivityEvent


def mood_for_event(event: ActivityEvent) -> str:
    if event.type in {"idle_15m"}:
        return "sleepy"
    if event.type == "return_from_idle":
        return "happy"
    if event.type in {"long_active_90m", "late_night_active"}:
        return "concerned"
    if event.type in {"long_active_25m", "long_active_45m"}:
        return "curious"
    return "calm"

