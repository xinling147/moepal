from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from companion_app.animation.actions import ACTIONS
from companion_app.core.pet_state import PetState
from companion_app.core.edge_pose import choose_edge_action
from companion_app.privacy import build_privacy_context


class CompanionController:
    _INTERACTION_ACTIONS = {
        "click": ("happy_bounce", "happy"),
        "tease": ("tail_wag", "happy"),
        "hover": ("look_around", "curious"),
    }

    def __init__(
        self,
        *,
        activity_tracker: Any,
        behavior_engine: Any,
        animator: Any,
        window: Any,
        speech_provider: Any,
        pet_state: PetState,
        bubble_enabled: bool = True,
        privacy_builder: Callable = build_privacy_context,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._activity_tracker = activity_tracker
        self._behavior_engine = behavior_engine
        self._animator = animator
        self._window = window
        self._speech_provider = speech_provider
        self._pet_state = pet_state
        self._bubble_enabled = bubble_enabled
        self._privacy_builder = privacy_builder
        self._clock = clock or datetime.now
        self._last_interaction_at: dict[str, datetime] = {}

    @property
    def pet_state(self) -> PetState:
        return self._pet_state

    def tick_behavior(self) -> None:
        event = self._activity_tracker.sample()
        decision = self._behavior_engine.decide(event, self._pet_state)

        self._animator.request_action(decision.action_id)
        self._pet_state.current_action = decision.action_id
        self._pet_state.mood = getattr(
            decision,
            "mood",
            self._infer_mood(decision.action_id, event),
        )

        if not self._bubble_enabled:
            return
        if not getattr(decision, "should_speak", False) or not decision.speech_intent:
            return

        context = self._privacy_builder(
            event.snapshot,
            self._pet_state,
            decision.action_id,
        )
        line = self._speech_provider.generate_companion_line(
            context=context,
            speech_intent=decision.speech_intent,
        )
        if line:
            self._window.show_bubble(line)

    def tick_animation(self, dt: float) -> None:
        self._animator.update(dt)
        frame = self._animator.get_current_frame()
        if frame is not None:
            self._window.set_frame(frame)

    def handle_edge_pose(self, edge: str, bottom_gap: int) -> None:
        action_id = choose_edge_action(edge, bottom_gap=bottom_gap)
        self._animator.request_action(action_id)
        self._pet_state.current_action = action_id

    def handle_user_interaction(self, interaction_type: str) -> None:
        action = self._INTERACTION_ACTIONS.get(interaction_type)
        if action is None or not self._interaction_allowed(interaction_type):
            return

        action_id, mood = action
        self._animator.request_action(action_id)
        self._pet_state.current_action = action_id
        self._pet_state.mood = mood
        self._pet_state.last_interaction_at = self._clock()

    def apply_runtime_settings(
        self,
        config: dict[str, Any],
        *,
        speech_provider: Any | None = None,
    ) -> None:
        self._bubble_enabled = bool(config.get("bubble_enabled", self._bubble_enabled))
        self._pet_state.personality = str(config.get("personality", self._pet_state.personality))
        if speech_provider is not None:
            self._speech_provider = speech_provider

    def request_manual_action(self, action_id: str) -> None:
        if action_id not in ACTIONS:
            return
        self._animator.request_action(action_id)
        self._pet_state.current_action = action_id
        self._pet_state.mood = self._mood_for_action(action_id)

    def _interaction_allowed(self, interaction_type: str) -> bool:
        now = self._clock()
        last = self._last_interaction_at.get(interaction_type)
        if last is not None and (now - last).total_seconds() < 1.5:
            return False
        self._last_interaction_at[interaction_type] = now
        return True

    @staticmethod
    def _infer_mood(action_id: str, event: Any) -> str:
        mood = CompanionController._mood_for_action(action_id)
        if mood != "calm":
            return mood
        if getattr(event, "type", "") == "return_from_idle":
            return "happy"
        return "calm"

    @staticmethod
    def _mood_for_action(action_id: str) -> str:
        if action_id == "concerned":
            return "concerned"
        if action_id in {"sleep", "sit_wait"}:
            return "sleepy"
        if action_id in {"wake_up", "tail_wag", "happy_bounce"}:
            return "happy"
        if action_id in {"look_around", "peek", "walk_edge"}:
            return "curious"
        return "calm"


__all__ = ["CompanionController"]
