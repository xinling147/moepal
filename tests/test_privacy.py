from dataclasses import asdict, dataclass, fields
from datetime import datetime


@dataclass(frozen=True)
class SnapshotStub:
    idle_seconds: int
    active_seconds: int
    returned_from_idle_seconds: int | None
    time_bucket: str
    timestamp: datetime
    app_name: str = "secret app"
    window_title: str = "secret title"
    file_name: str = "secret.txt"
    file_path: str = "C:/Users/example/secret.txt"
    keyboard_input: str = "typed secret"
    browser_content: str = "private page"
    chat_content: str = "private chat"
    screenshot: bytes = b"private pixels"


@dataclass(frozen=True)
class PetStateStub:
    personality: str
    mood: str
    current_action: str
    last_interaction_at: datetime | None


FORBIDDEN_FIELDS = {
    "app_name",
    "window_title",
    "file_name",
    "file_path",
    "keyboard_input",
    "browser_content",
    "chat_content",
    "screenshot",
}


def test_build_privacy_context_maps_allowed_fields_and_floors_minutes():
    from companion_app.privacy import build_privacy_context

    snapshot = SnapshotStub(
        idle_seconds=119,
        active_seconds=125,
        returned_from_idle_seconds=361,
        time_bucket="late_night",
        timestamp=datetime(2026, 5, 2, 23, 30, 0),
    )
    state = PetStateStub(
        personality="gentle",
        mood="concerned",
        current_action="idle_lie",
        last_interaction_at=None,
    )

    context = build_privacy_context(snapshot, state, action_id="concerned")

    assert asdict(context) == {
        "active_minutes": 2,
        "idle_minutes": 1,
        "returned_from_idle_minutes": 6,
        "time_bucket": "late_night",
        "personality": "gentle",
        "mood": "concerned",
        "action_id": "concerned",
    }


def test_build_privacy_context_preserves_none_returned_from_idle():
    from companion_app.privacy import build_privacy_context

    snapshot = SnapshotStub(
        idle_seconds=0,
        active_seconds=60,
        returned_from_idle_seconds=None,
        time_bucket="morning",
        timestamp=datetime(2026, 5, 2, 9, 0, 0),
    )
    state = PetStateStub(
        personality="quiet",
        mood="calm",
        current_action="idle_lie",
        last_interaction_at=None,
    )

    context = build_privacy_context(snapshot, state, action_id="idle_lie")

    assert context.returned_from_idle_minutes is None


def test_privacy_context_exposes_only_whitelisted_fields():
    from companion_app.privacy import PrivacyContext, build_privacy_context

    snapshot = SnapshotStub(
        idle_seconds=30,
        active_seconds=30,
        returned_from_idle_seconds=None,
        time_bucket="afternoon",
        timestamp=datetime(2026, 5, 2, 15, 0, 0),
    )
    state = PetStateStub(
        personality="lively",
        mood="happy",
        current_action="wave",
        last_interaction_at=None,
    )

    context = build_privacy_context(snapshot, state, action_id="wave")
    field_names = {field.name for field in fields(PrivacyContext)}

    assert field_names == set(asdict(context).keys())
    assert FORBIDDEN_FIELDS.isdisjoint(field_names)
    assert FORBIDDEN_FIELDS.isdisjoint(asdict(context).keys())
