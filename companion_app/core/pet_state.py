from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PetState:
    personality: str = "gentle"
    mood: str = "calm"
    current_action: str = "idle_lie"
    last_interaction_at: datetime | None = None

