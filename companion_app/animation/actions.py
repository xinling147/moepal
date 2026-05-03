from dataclasses import dataclass


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    loop: bool
    interruptible: bool
    fps: int
    fallback_action_id: str


ACTIONS: dict[str, ActionDefinition] = {
    "idle_lie": ActionDefinition(
        action_id="idle_lie",
        loop=True,
        interruptible=True,
        fps=4,
        fallback_action_id="idle_lie",
    ),
    "tail_wag": ActionDefinition(
        action_id="tail_wag",
        loop=True,
        interruptible=True,
        fps=8,
        fallback_action_id="idle_lie",
    ),
    "sleep": ActionDefinition(
        action_id="sleep",
        loop=True,
        interruptible=True,
        fps=2,
        fallback_action_id="idle_lie",
    ),
    "wake_up": ActionDefinition(
        action_id="wake_up",
        loop=False,
        interruptible=False,
        fps=6,
        fallback_action_id="idle_lie",
    ),
    "stretch": ActionDefinition(
        action_id="stretch",
        loop=False,
        interruptible=True,
        fps=6,
        fallback_action_id="idle_lie",
    ),
    "look_around": ActionDefinition(
        action_id="look_around",
        loop=True,
        interruptible=True,
        fps=6,
        fallback_action_id="idle_lie",
    ),
    "nudge": ActionDefinition(
        action_id="nudge",
        loop=False,
        interruptible=True,
        fps=6,
        fallback_action_id="idle_lie",
    ),
    "concerned": ActionDefinition(
        action_id="concerned",
        loop=False,
        interruptible=True,
        fps=4,
        fallback_action_id="idle_lie",
    ),
    "happy_bounce": ActionDefinition(
        action_id="happy_bounce",
        loop=False,
        interruptible=True,
        fps=8,
        fallback_action_id="idle_lie",
    ),
    "peek": ActionDefinition(
        action_id="peek",
        loop=True,
        interruptible=True,
        fps=6,
        fallback_action_id="idle_lie",
    ),
    "walk_edge": ActionDefinition(
        action_id="walk_edge",
        loop=False,
        interruptible=False,
        fps=8,
        fallback_action_id="idle_lie",
    ),
    "sit_wait": ActionDefinition(
        action_id="sit_wait",
        loop=True,
        interruptible=True,
        fps=4,
        fallback_action_id="idle_lie",
    ),
}

_EXPECTED_ACTION_IDS = frozenset({
    "idle_lie", "tail_wag", "sleep", "wake_up",
    "stretch", "look_around", "nudge", "concerned",
    "happy_bounce", "peek", "walk_edge", "sit_wait",
})
assert _EXPECTED_ACTION_IDS == set(ACTIONS.keys()), \
    f"Action registry mismatch: missing={_EXPECTED_ACTION_IDS - set(ACTIONS.keys())}, extra={set(ACTIONS.keys()) - _EXPECTED_ACTION_IDS}"
