import os
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class ContextStub:
    active_minutes: int = 45
    idle_minutes: int = 0
    returned_from_idle_minutes: int | None = None
    time_bucket: str = "afternoon"
    personality: str = "gentle"
    mood: str = "calm"
    action_id: str = "nudge"


KNOWN_INTENTS = [
    "welcome_back",
    "soft_checkin",
    "rest_reminder",
    "strong_rest_reminder",
    "late_night_care",
]


@pytest.fixture()
def provider():
    from companion_app.ai.fallback_provider import FallbackLineProvider

    return FallbackLineProvider()


@pytest.mark.parametrize("speech_intent", KNOWN_INTENTS)
def test_generate_companion_line_returns_short_readable_chinese_line(provider, speech_intent):
    line = provider.generate_companion_line(
        context=ContextStub(),
        speech_intent=speech_intent,
    )

    assert isinstance(line, str)
    assert line
    assert len(line) <= 28
    assert any("\u4e00" <= char <= "\u9fff" for char in line)
    assert "�" not in line


@pytest.mark.parametrize(
    ("speech_intent", "expected_fragment"),
    [
        ("welcome_back", "回来"),
        ("soft_checkin", "慢慢来"),
        ("rest_reminder", "伸个懒腰"),
        ("strong_rest_reminder", "担心你"),
        ("late_night_care", "夜深了"),
    ],
)
def test_known_intents_have_matching_gentle_copy(provider, speech_intent, expected_fragment):
    line = provider.generate_companion_line(ContextStub(), speech_intent)

    assert expected_fragment in line
    assert "必须" not in line
    assert "快去" not in line
    assert "怎么还" not in line


def test_unknown_intent_returns_safe_short_line(provider):
    line = provider.generate_companion_line(ContextStub(), "not_registered")

    assert line == "我在这里陪你。"
    assert len(line) <= 28


def test_provider_does_not_require_environment_or_network(provider, monkeypatch):
    monkeypatch.setattr(os, "environ", {})

    line = provider.generate_companion_line(
        context=ContextStub(active_minutes=90),
        speech_intent="rest_reminder",
        timeout_seconds=0,
    )

    assert line
    assert len(line) <= 28
