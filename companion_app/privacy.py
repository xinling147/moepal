from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from companion_app.activity.session_tracker import ActivitySnapshot
    from companion_app.core.pet_state import PetState


@dataclass(frozen=True)
class PrivacyContext:
    active_minutes: int
    idle_minutes: int
    returned_from_idle_minutes: int | None
    time_bucket: str
    personality: str
    mood: str
    action_id: str


def build_privacy_context(
    snapshot: ActivitySnapshot,
    pet_state: PetState,
    action_id: str,
) -> PrivacyContext:
    returned_seconds = snapshot.returned_from_idle_seconds

    return PrivacyContext(
        active_minutes=snapshot.active_seconds // 60,
        idle_minutes=snapshot.idle_seconds // 60,
        returned_from_idle_minutes=(
            None if returned_seconds is None else returned_seconds // 60
        ),
        time_bucket=snapshot.time_bucket,
        personality=pet_state.personality,
        mood=pet_state.mood,
        action_id=action_id,
    )


__all__ = ["PrivacyContext", "build_privacy_context"]
