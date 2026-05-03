import pytest

from companion_app.animation.actions import ACTIONS, ActionDefinition

_EXPECTED_IDS = frozenset({
    "idle_lie", "tail_wag", "sleep", "wake_up",
    "stretch", "look_around", "nudge", "concerned",
    "happy_bounce", "peek", "walk_edge", "sit_wait",
})


# ---- TC-8: 12 个动作 ID 全部存在 --------------------------------------------

def test_all_12_action_ids_are_defined():
    actual_ids = set(ACTIONS.keys())
    assert actual_ids == _EXPECTED_IDS, \
        f"missing={_EXPECTED_IDS - actual_ids}, extra={actual_ids - _EXPECTED_IDS}"


# ---- TC-9: 每个动作定义字段完整 ----------------------------------------------

def test_every_action_definition_has_required_fields():
    for action_id, ad in ACTIONS.items():
        assert ad.action_id == action_id
        assert isinstance(ad.loop, bool)
        assert isinstance(ad.interruptible, bool)
        assert isinstance(ad.fps, int) and ad.fps > 0
        assert isinstance(ad.fallback_action_id, str) and ad.fallback_action_id


# ---- TC-12: fallback_action_id 指向已定义动作 --------------------------------

def test_fallback_action_id_refers_to_defined_action():
    for ad in ACTIONS.values():
        assert ad.fallback_action_id in ACTIONS, \
            f"{ad.action_id}.fallback_action_id={ad.fallback_action_id} is not a known action"


# ---- TC-10: 循环/一次性分类符合预期 ------------------------------------------

def test_loop_flag_matches_action_semantics():
    """Actions that represent continuous states should loop."""
    looping_actions = {"idle_lie", "tail_wag", "sleep", "look_around", "peek", "sit_wait"}
    one_shot_actions = _EXPECTED_IDS - looping_actions

    for aid in looping_actions:
        assert ACTIONS[aid].loop is True, f"{aid} should be looping"

    for aid in one_shot_actions:
        assert ACTIONS[aid].loop is False, f"{aid} should be one-shot"


# ---- TC-11: 可打断标记符合预期 -----------------------------------------------

def test_interruptible_flag_is_correctly_set():
    """Most actions are interruptible; wake_up and walk_edge are not."""
    non_interruptible = {"wake_up", "walk_edge"}

    for aid in _EXPECTED_IDS:
        if aid in non_interruptible:
            assert ACTIONS[aid].interruptible is False, f"{aid} should NOT be interruptible"
        else:
            assert ACTIONS[aid].interruptible is True, f"{aid} should be interruptible"
