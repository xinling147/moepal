def test_build_speech_provider_uses_fallback_when_ai_disabled():
    from companion_app.ai.fallback_provider import FallbackLineProvider
    from companion_app.runtime import build_speech_provider

    provider = build_speech_provider({"ai_enabled": False, "ai_provider": "deepseek"})

    assert isinstance(provider, FallbackLineProvider)


def test_build_speech_provider_wraps_deepseek_with_fallback_when_ai_enabled():
    from companion_app.ai.deepseek_provider import DeepSeekAnthropicProvider
    from companion_app.ai.provider import FallbackOnNoneProvider
    from companion_app.runtime import build_speech_provider

    provider = build_speech_provider({"ai_enabled": True, "ai_provider": "deepseek"})

    assert isinstance(provider, FallbackOnNoneProvider)
    assert isinstance(provider._primary, DeepSeekAnthropicProvider)


def test_build_speech_provider_ignores_api_keys_in_config(monkeypatch):
    from companion_app.runtime import build_speech_provider

    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fallback-env-key")

    provider = build_speech_provider(
        {
            "ai_enabled": True,
            "ai_provider": "deepseek",
            "anthropic_api_key": "config-key",
            "deepseek_api_key": "config-deepseek-key",
        }
    )

    assert provider._primary._read_api_key() == "env-key"


def test_build_speech_provider_falls_back_for_unknown_provider():
    from companion_app.ai.fallback_provider import FallbackLineProvider
    from companion_app.runtime import build_speech_provider

    provider = build_speech_provider({"ai_enabled": True, "ai_provider": "unknown"})

    assert isinstance(provider, FallbackLineProvider)


def test_build_async_speech_provider_uses_async_deepseek_when_ai_enabled():
    from companion_app.ai.async_provider import AsyncSpeechProvider
    from companion_app.ai.deepseek_provider import DeepSeekAnthropicProvider
    from companion_app.runtime import build_async_speech_provider

    provider = build_async_speech_provider(
        {"ai_enabled": True, "ai_provider": "deepseek"},
        on_line=lambda _line: None,
    )

    assert isinstance(provider, AsyncSpeechProvider)
    assert isinstance(provider._primary, DeepSeekAnthropicProvider)


def test_build_async_speech_provider_uses_fallback_when_ai_disabled():
    from companion_app.ai.fallback_provider import FallbackLineProvider
    from companion_app.runtime import build_async_speech_provider

    provider = build_async_speech_provider(
        {"ai_enabled": False, "ai_provider": "deepseek"},
        on_line=lambda _line: None,
    )

    assert isinstance(provider, FallbackLineProvider)
