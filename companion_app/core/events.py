from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from companion_app.activity.session_tracker import ActivitySnapshot
else:
    ActivitySnapshot = Any


@dataclass(frozen=True)
class ActivityEvent:
    type: str
    snapshot: ActivitySnapshot

