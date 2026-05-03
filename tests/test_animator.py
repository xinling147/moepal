"""Tests for companion_app.animation.animator — animation state machine.

Uses fake string frames injected via frame_loader.  Zero Qt dependency.
"""

import pytest

from companion_app.animation.actions import ACTIONS
from companion_app.animation.animator import Animator


def _make_fake_loader(actions: dict[str, list] | None = None):
    """Return a frame loader that returns fake string frames.

    Default: each action gets 3 frames like ["idle_lie/0", "idle_lie/1", …].
    """
    if actions is None:
        actions = {}
    defaults = {
        "idle_lie": ["idle_lie/0", "idle_lie/1", "idle_lie/2"],
        "nudge": ["nudge/0", "nudge/1", "nudge/2"],
        "tail_wag": ["tail_wag/0", "tail_wag/1", "tail_wag/2"],
        "wake_up": ["wake_up/0", "wake_up/1", "wake_up/2"],
    }

    def _loader(action_id: str) -> list:
        if action_id in actions:
            return list(actions[action_id])
        if action_id in defaults:
            return list(defaults[action_id])
        # Generate generic frames for unknown actions from the real catalog
        count = 3
        if action_id in ACTIONS:
            count = ACTIONS[action_id].fps
        return [f"{action_id}/{i}" for i in range(count)]

    return _loader


# ---- TC-22: Animator 初始状态为 idle_lie ------------------------------------

def test_animator_initializes_with_idle_lie():
    loader = _make_fake_loader()
    anim = Animator(loader)
    assert anim.current_action_id == "idle_lie"


# ---- TC-18: 一次性动作播放结束后回到 fallback 动作 ---------------------------

def test_one_shot_action_returns_to_fallback_after_completion():
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="idle_lie")
    assert anim.current_action_id == "idle_lie"

    anim.request_action("nudge")
    assert anim.current_action_id == "nudge"

    fps = ACTIONS["nudge"].fps
    dt = 1.0 / fps

    for _ in range(3):
        anim.update(dt)

    assert anim.current_action_id == "idle_lie"


# ---- TC-19: 可打断动作可以被高优先级动作中断 --------------------------------

def test_interruptible_action_can_be_interrupted():
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="idle_lie")
    anim.request_action("tail_wag")
    assert anim.current_action_id == "tail_wag"


# ---- TC-20: 不可打断动作不能被中断 ------------------------------------------

def test_non_interruptible_action_is_not_interrupted():
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="idle_lie")
    assert ACTIONS["wake_up"].interruptible is False

    anim.request_action("wake_up")
    assert anim.current_action_id == "wake_up"

    anim.request_action("nudge")
    # wake_up is non-interruptible, still playing
    assert anim.current_action_id == "wake_up"

    fps = ACTIONS["wake_up"].fps
    dt = 1.0 / fps
    for _ in range(3):
        anim.update(dt)

    # After wake_up completes, queued nudge takes over
    assert anim.current_action_id == "nudge"


# ---- TC-21: 循环动作持续返回当前帧 ------------------------------------------

def test_looping_action_loops_indefinitely():
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="idle_lie")

    frame = anim.get_current_frame()
    assert frame == "idle_lie/0"

    fps = 4
    dt = 1.0 / fps

    for _ in range(12):
        anim.update(dt)
        f = anim.get_current_frame()
        assert f is not None
        assert f.startswith("idle_lie/")

    assert anim.current_action_id == "idle_lie"


def test_requesting_current_action_does_not_reset_frame_or_reload():
    load_calls: list[str] = []

    def loader(action_id: str) -> list[str]:
        load_calls.append(action_id)
        return [f"{action_id}/0", f"{action_id}/1", f"{action_id}/2"]

    anim = Animator(loader, initial_action="idle_lie")
    anim.update(1.0 / ACTIONS["idle_lie"].fps)
    assert anim.get_current_frame() == "idle_lie/1"

    anim.request_action("idle_lie")

    assert anim.get_current_frame() == "idle_lie/1"
    assert load_calls == ["idle_lie"]


# ---- TC-23: 请求不存在的动作 ID 不崩溃 --------------------------------------

def test_request_unknown_action_does_not_crash(caplog):
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="idle_lie")
    anim.request_action("nonexistent_action")

    assert anim.current_action_id == "idle_lie"
    assert any("unknown" in r.message.lower() for r in caplog.records)


# ---- TC-24: 帧更新速率 (fps) 影响帧切换 -------------------------------------

def test_frame_advance_respects_fps_timing():
    loader = _make_fake_loader()
    anim = Animator(loader, initial_action="tail_wag")
    fps = ACTIONS["tail_wag"].fps
    dt = 1.0 / fps

    # Not enough time to advance
    frame0 = anim.get_current_frame()
    anim.update(dt * 0.4)
    frame_half = anim.get_current_frame()
    assert frame_half == frame0

    # Full frame duration — should advance
    anim.update(dt * 0.4)
    frame_one = anim.get_current_frame()
    # After 0.8 * dt total, still not enough for a full frame; need 1.0
    # Actually: 0.4 + 0.4 = 0.8, which is < 1.0, so no advance yet
    # Let's do one more partial update
    anim.update(dt * 0.3)
    # Now elapsed = 0.8 + 0.3 = 1.1 dt, one advance
    frame_advanced = anim.get_current_frame()
    assert frame_advanced != frame0


# ---- TC-27: get_current_frame 在无帧时返回 None ----------------------------

def test_get_current_frame_returns_none_when_no_frames():
    empty_loader = lambda _aid: []
    anim = Animator(empty_loader, initial_action="idle_lie")
    assert anim.get_current_frame() is None
    assert anim.frame_count == 0


# ---- TC-28: 帧数为 0 时 update 不崩溃 ---------------------------------------

def test_update_does_not_crash_with_zero_frames():
    empty_loader = lambda _aid: []
    anim = Animator(empty_loader, initial_action="idle_lie")
    anim.update(1.0)  # must not raise
