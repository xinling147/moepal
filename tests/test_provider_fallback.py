from dataclasses import dataclass


@dataclass(frozen=True)
class ContextStub:
    active_minutes: int = 1
    idle_minutes: int = 0
    returned_from_idle_minutes: int | None = None
    time_bucket: str = "afternoon"
    personality: str = "gentle"
    mood: str = "calm"
    action_id: str = "idle_lie"


class ProviderStub:
    def __init__(self, line=None, exc=None):
        self.line = line
        self.exc = exc
        self.calls = []

    def generate_companion_line(self, context, speech_intent, timeout_seconds=8):
        self.calls.append((context, speech_intent, timeout_seconds))
        if self.exc is not None:
            raise self.exc
        return self.line


def test_fallback_on_none_provider_uses_primary_line_when_available():
    from companion_app.ai.provider import FallbackOnNoneProvider

    primary = ProviderStub(line="primary")
    fallback = ProviderStub(line="fallback")
    context = ContextStub()

    provider = FallbackOnNoneProvider(primary, fallback)

    assert provider.generate_companion_line(context, "rest_reminder", 3) == "primary"
    assert primary.calls == [(context, "rest_reminder", 3)]
    assert fallback.calls == []


def test_fallback_on_none_provider_uses_fallback_for_none_or_exception():
    from companion_app.ai.provider import FallbackOnNoneProvider

    context = ContextStub()

    provider = FallbackOnNoneProvider(
        ProviderStub(line=None),
        ProviderStub(line="fallback"),
    )
    assert provider.generate_companion_line(context, "rest_reminder") == "fallback"

    provider = FallbackOnNoneProvider(
        ProviderStub(exc=TimeoutError("offline")),
        ProviderStub(line="fallback"),
    )
    assert provider.generate_companion_line(context, "rest_reminder") == "fallback"
