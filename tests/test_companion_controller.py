from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from companion_app.core.events import ActivityEvent
from companion_app.core.pet_state import PetState
from companion_app.privacy import build_privacy_context


@dataclass(frozen=True)
class SnapshotStub:
    idle_seconds: int = 0
    active_seconds: int = 0
    returned_from_idle_seconds: int | None = None
    time_bucket: str = "afternoon"
    timestamp: datetime = datetime(2026, 5, 3, 15, 0, 0)
    app_name: str = "private app"
    window_title: str = "private title"
    keyboard_input: str = "private input"


class FakeTracker:
    def __init__(self, event: ActivityEvent) -> None:
        self.event = event
        self.sample_calls = 0

    def sample(self) -> ActivityEvent:
        self.sample_calls += 1
        return self.event


class FakeBehaviorEngine:
    def __init__(self, decision: SimpleNamespace) -> None:
        self.decision = decision
        self.calls: list[tuple[ActivityEvent, PetState]] = []

    def decide(self, event: ActivityEvent, pet_state: PetState) -> SimpleNamespace:
        self.calls.append((event, pet_state))
        return self.decision


class FakeAnimator:
    def __init__(self, frame: object | None = "frame-0") -> None:
        self.frame = frame
        self.requested_actions: list[str] = []
        self.update_calls: list[float] = []

    def request_action(self, action_id: str) -> None:
        self.requested_actions.append(action_id)

    def update(self, dt: float) -> None:
        self.update_calls.append(dt)

    def get_current_frame(self) -> object | None:
        return self.frame


class FakeWindow:
    def __init__(self) -> None:
        self.frames: list[object] = []
        self.bubbles: list[str] = []

    def set_frame(self, frame: object) -> None:
        self.frames.append(frame)

    def show_bubble(self, text: str) -> None:
        self.bubbles.append(text)


class FakeSpeechProvider:
    def __init__(self, line: str | None = "该休息一下啦") -> None:
        self.line = line
        self.calls: list[dict[str, object]] = []

    def generate_companion_line(
        self,
        *,
        context: object,
        speech_intent: str,
    ) -> str | None:
        self.calls.append(
            {
                "context": context,
                "speech_intent": speech_intent,
            }
        )
        return self.line


def _decision(
    *,
    action_id: str = "nudge",
    should_speak: bool = False,
    speech_intent: str | None = None,
    mood: str = "attentive",
) -> SimpleNamespace:
    return SimpleNamespace(
        action_id=action_id,
        should_speak=should_speak,
        speech_intent=speech_intent,
        mood=mood,
    )


def _event(snapshot: SnapshotStub | None = None, event_type: str = "active_tick"):
    return ActivityEvent(type=event_type, snapshot=snapshot or SnapshotStub())


def _controller(
    *,
    event: ActivityEvent | None = None,
    decision: SimpleNamespace | None = None,
    animator: FakeAnimator | None = None,
    window: FakeWindow | None = None,
    provider: FakeSpeechProvider | None = None,
    state: PetState | None = None,
    bubble_enabled: bool = True,
    clock=None,
):
    from companion_app.core.controller import CompanionController

    tracker = FakeTracker(event or _event())
    engine = FakeBehaviorEngine(decision or _decision())
    animator = animator or FakeAnimator()
    window = window or FakeWindow()
    provider = provider or FakeSpeechProvider()
    state = state or PetState(personality="gentle", mood="calm")

    controller = CompanionController(
        activity_tracker=tracker,
        behavior_engine=engine,
        animator=animator,
        window=window,
        speech_provider=provider,
        pet_state=state,
        bubble_enabled=bubble_enabled,
        clock=clock,
    )
    return controller, tracker, engine, animator, window, provider, state


def test_tick_behavior_without_speech_requests_action_but_skips_provider_and_bubble():
    decision = _decision(
        action_id="sit_wait",
        should_speak=False,
        speech_intent=None,
        mood="calm",
    )
    controller, tracker, engine, animator, window, provider, state = _controller(
        event=_event(event_type="idle_5m"),
        decision=decision,
    )

    controller.tick_behavior()

    assert tracker.sample_calls == 1
    assert engine.calls == [(tracker.event, state)]
    assert animator.requested_actions == ["sit_wait"]
    assert provider.calls == []
    assert window.bubbles == []


def test_tick_behavior_speaks_with_privacy_context_when_bubble_enabled():
    snapshot = SnapshotStub(active_seconds=46 * 60, idle_seconds=0)
    event = _event(snapshot=snapshot, event_type="long_active_45m")
    decision = _decision(
        action_id="nudge",
        should_speak=True,
        speech_intent="rest_reminder",
        mood="concerned",
    )
    state = PetState(personality="gentle", mood="calm", current_action="idle_lie")
    provider = FakeSpeechProvider(line="起来走两步吧")
    controller, _, _, animator, window, provider, state = _controller(
        event=event,
        decision=decision,
        provider=provider,
        state=state,
        bubble_enabled=True,
    )

    controller.tick_behavior()

    assert animator.requested_actions == ["nudge"]
    assert provider.calls == [
        {
            "context": build_privacy_context(snapshot, state, action_id="nudge"),
            "speech_intent": "rest_reminder",
        }
    ]
    assert window.bubbles == ["起来走两步吧"]


@pytest.mark.parametrize("line", [None, ""])
def test_tick_behavior_does_not_show_bubble_when_provider_returns_empty_line(line):
    controller, _, _, _, window, provider, _ = _controller(
        decision=_decision(
            action_id="wake_up",
            should_speak=True,
            speech_intent="welcome_back",
            mood="happy",
        ),
        provider=FakeSpeechProvider(line=line),
    )

    controller.tick_behavior()

    assert provider.calls
    assert window.bubbles == []


def test_tick_animation_sets_current_frame_after_animator_update():
    animator = FakeAnimator(frame="frame-1")
    controller, _, _, animator, window, _, _ = _controller(animator=animator)

    controller.tick_animation(0.25)

    assert animator.update_calls == [0.25]
    assert window.frames == ["frame-1"]


def test_tick_animation_skips_window_update_when_animator_has_no_frame():
    animator = FakeAnimator(frame=None)
    controller, _, _, animator, window, _, _ = _controller(animator=animator)

    controller.tick_animation(0.25)

    assert animator.update_calls == [0.25]
    assert window.frames == []


def test_handle_edge_pose_requests_pose_action_for_current_edge():
    animator = FakeAnimator()
    controller, _, _, animator, _, _, state = _controller(animator=animator)

    controller.handle_edge_pose("right", bottom_gap=180)

    assert animator.requested_actions == ["walk_edge"]
    assert state.current_action == "walk_edge"


def test_handle_user_interaction_click_triggers_happy_bounce():
    animator = FakeAnimator()
    state = PetState(personality="gentle", mood="calm", current_action="idle_lie")
    controller, _, _, animator, _, _, state = _controller(
        animator=animator,
        state=state,
    )

    controller.handle_user_interaction("click")

    assert animator.requested_actions == ["happy_bounce"]
    assert state.current_action == "happy_bounce"
    assert state.mood == "happy"


def test_handle_user_interaction_tease_triggers_tail_wag():
    animator = FakeAnimator()
    controller, _, _, animator, _, _, state = _controller(animator=animator)

    controller.handle_user_interaction("tease")

    assert animator.requested_actions == ["tail_wag"]
    assert state.current_action == "tail_wag"
    assert state.mood == "happy"


def test_handle_user_interaction_hover_triggers_look_around():
    animator = FakeAnimator()
    controller, _, _, animator, _, _, state = _controller(animator=animator)

    controller.handle_user_interaction("hover")

    assert animator.requested_actions == ["look_around"]
    assert state.current_action == "look_around"
    assert state.mood == "curious"


def test_handle_user_interaction_throttles_repeated_mouse_events():
    now = datetime(2026, 5, 3, 15, 0, 0)

    def clock():
        return now

    animator = FakeAnimator()
    controller, _, _, animator, _, _, _ = _controller(animator=animator, clock=clock)

    controller.handle_user_interaction("tease")
    controller.handle_user_interaction("tease")
    now += timedelta(seconds=2)
    controller.handle_user_interaction("tease")

    assert animator.requested_actions == ["tail_wag", "tail_wag"]


def test_tick_behavior_updates_pet_state_current_action_and_mood():
    state = PetState(personality="gentle", mood="calm", current_action="idle_lie")
    controller, _, _, _, _, _, state = _controller(
        decision=_decision(
            action_id="concerned",
            should_speak=False,
            speech_intent=None,
            mood="concerned",
        ),
        state=state,
    )

    controller.tick_behavior()

    assert state.current_action == "concerned"
    assert state.mood == "concerned"


def test_apply_runtime_settings_updates_personality_bubbles_and_provider():
    original_provider = FakeSpeechProvider(line="old")
    new_provider = FakeSpeechProvider(line="new")
    state = PetState(personality="gentle", mood="calm")
    controller, _, _, _, _, _, state = _controller(
        provider=original_provider,
        state=state,
        bubble_enabled=True,
    )

    controller.apply_runtime_settings(
        {"personality": "lively", "bubble_enabled": False},
        speech_provider=new_provider,
    )

    assert state.personality == "lively"
    assert controller._bubble_enabled is False
    assert controller._speech_provider is new_provider
