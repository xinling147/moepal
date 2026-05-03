from dataclasses import dataclass


@dataclass(frozen=True)
class ContextStub:
    active_minutes: int = 45
    idle_minutes: int = 0
    returned_from_idle_minutes: int | None = None
    time_bucket: str = "afternoon"
    personality: str = "gentle"
    mood: str = "calm"
    action_id: str = "nudge"


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


class CapturingExecutor:
    def __init__(self):
        self.jobs = []

    def submit(self, fn):
        self.jobs.append(fn)


def test_async_speech_provider_returns_immediately_and_runs_later():
    from companion_app.ai.async_provider import AsyncSpeechProvider

    executor = CapturingExecutor()
    callback_lines = []
    context = ContextStub()
    primary = ProviderStub(line="primary")
    fallback = ProviderStub(line="fallback")

    provider = AsyncSpeechProvider(primary, fallback, callback_lines.append, executor=executor)

    result = provider.generate_companion_line(context, "rest_reminder", 2)

    assert result is None
    assert primary.calls == []
    assert len(executor.jobs) == 1

    executor.jobs[0]()

    assert primary.calls == [(context, "rest_reminder", 2)]
    assert fallback.calls == []
    assert callback_lines == ["primary"]


def test_async_speech_provider_uses_fallback_for_none_or_exception():
    from companion_app.ai.async_provider import AsyncSpeechProvider

    for primary in [ProviderStub(line=None), ProviderStub(exc=TimeoutError("offline"))]:
        executor = CapturingExecutor()
        callback_lines = []
        fallback = ProviderStub(line="fallback")

        provider = AsyncSpeechProvider(
            primary,
            fallback,
            callback_lines.append,
            executor=executor,
        )
        provider.generate_companion_line(ContextStub(), "rest_reminder")
        executor.jobs[0]()

        assert fallback.calls
        assert callback_lines == ["fallback"]
