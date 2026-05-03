from __future__ import annotations

import logging
from collections.abc import Callable

from .actions import ACTIONS, ActionDefinition

logger = logging.getLogger(__name__)

# Frame loader: takes action_id, returns list of frame objects.
FrameLoader = Callable[[str], list]


class Animator:
    """Animation state machine driven by a pluggable frame loader.

    Frames are opaque objects; the Animator only stores and indexes them.
    The meaning of a frame is defined by the loader, for example QPixmap or str.
    """

    def __init__(
        self,
        frame_loader: FrameLoader,
        initial_action: str = "idle_lie",
    ):
        if initial_action not in ACTIONS:
            logger.warning("Unknown initial action '%s', using idle_lie.", initial_action)
            initial_action = "idle_lie"

        self._frame_loader = frame_loader
        self._current_action_id: str = initial_action
        self._current_action_def: ActionDefinition = ACTIONS[initial_action]
        self._frames: list = self._frame_loader(initial_action)
        self._frame_index: int = 0
        self._elapsed: float = 0.0
        self._pending_action_id: str | None = None

    @property
    def current_action_id(self) -> str:
        return self._current_action_id

    @property
    def is_interruptible(self) -> bool:
        return self._current_action_def.interruptible

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def request_action(self, action_id: str) -> None:
        if action_id not in ACTIONS:
            logger.warning("Unknown action '%s', ignoring.", action_id)
            return

        if not self._current_action_def.interruptible:
            logger.debug(
                "Action '%s' is not interruptible, queuing '%s'.",
                self._current_action_id,
                action_id,
            )
            self._pending_action_id = action_id
            return

        self._switch_to(action_id)

    def get_current_frame(self):
        if not self._frames:
            return None
        return self._frames[self._frame_index]

    def update(self, dt: float) -> None:
        if not self._frames or self._current_action_def.fps <= 0:
            return

        self._elapsed += dt
        frame_duration = 1.0 / self._current_action_def.fps

        while self._elapsed >= frame_duration:
            self._elapsed -= frame_duration
            self._frame_index += 1

            if self._frame_index >= len(self._frames):
                if self._current_action_def.loop:
                    self._frame_index = 0
                else:
                    fallback = self._pending_action_id or self._current_action_def.fallback_action_id
                    self._switch_to(fallback)
                    return

    def _switch_to(self, action_id: str) -> None:
        self._current_action_id = action_id
        self._current_action_def = ACTIONS[action_id]
        self._frames = self._frame_loader(action_id)
        self._frame_index = 0
        self._elapsed = 0.0
        self._pending_action_id = None
