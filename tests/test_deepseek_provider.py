import json
from dataclasses import asdict

import pytest

from companion_app.privacy import PrivacyContext


DEFAULT_BASE_URL = "https://api.deepseek.com/anthropic"
FORBIDDEN_FIELD_NAMES = {
    "app_name",
    "window_title",
    "file_path",
    "file_name",
    "keyboard_input",
    "browser_content",
    "chat_content",
    "screenshot",
}
FORBIDDEN_VALUES = {
    "secret app",
    "secret title",
    "C:/Users/example/secret.txt",
    "secret.txt",
    "typed secret",
    "private page",
    "private chat",
    "private pixels",
}


class FakeTransport:
    def __init__(self, response=None, exc=None):
        self.response = response if response is not None else {
            "content": [{"type": "text", "text": "take a break"}]
        }
        self.exc = exc
        self.calls = []

    def post(self, url, *, headers, json, timeout):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "payload": json,
                "timeout": timeout,
            }
        )
        if self.exc is not None:
            raise self.exc
        return self.response


@pytest.fixture()
def privacy_context():
    return PrivacyContext(
        active_minutes=52,
        idle_minutes=0,
        returned_from_idle_minutes=18,
        time_bucket="late_night",
        personality="gentle",
        mood="concerned",
        action_id="concerned",
    )


def _provider_class():
    from companion_app.ai.deepseek_provider import DeepSeekAnthropicProvider

    return DeepSeekAnthropicProvider


def test_missing_api_key_is_catchable_and_does_not_call_transport(monkeypatch, privacy_context):
    from companion_app.ai import deepseek_provider as module

    provider_class = module.DeepSeekAnthropicProvider
    config_error = getattr(module, "ProviderConfigurationError", RuntimeError)
    transport = FakeTransport()
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    provider = provider_class(transport=transport)

    try:
        line = provider.generate_companion_line(
            context=privacy_context,
            speech_intent="rest_reminder",
        )
    except config_error:
        line = None

    assert line is None
    assert transport.calls == []


def test_api_key_prefers_anthropic_env_and_falls_back_to_deepseek_env(
    monkeypatch,
    privacy_context,
):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
    transport = FakeTransport()

    provider = provider_class(transport=transport)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    headers_json = json.dumps(transport.calls[0]["headers"])
    assert "anthropic-key" in headers_json
    assert "deepseek-key" not in headers_json

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    transport = FakeTransport()
    provider = provider_class(transport=transport)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    headers_json = json.dumps(transport.calls[0]["headers"])
    assert "deepseek-key" in headers_json


def test_uses_default_base_url_and_allows_anthropic_base_url_override(
    monkeypatch,
    privacy_context,
):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    transport = FakeTransport()

    provider = provider_class(transport=transport)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    assert transport.calls[0]["url"] == f"{DEFAULT_BASE_URL}/v1/messages"

    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://example.test/custom")
    transport = FakeTransport()
    provider = provider_class(transport=transport)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    assert transport.calls[0]["url"] == "https://example.test/custom/v1/messages"


def test_payload_uses_anthropic_messages_shape_with_default_deepseek_model(
    monkeypatch,
    privacy_context,
):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    transport = FakeTransport()

    provider = provider_class(transport=transport, timeout_seconds=7)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="strong_rest_reminder",
    )

    call = transport.calls[0]
    payload = call["payload"]
    assert call["timeout"] == 7
    assert {"model", "max_tokens", "system", "messages"}.issubset(set(payload))
    assert payload["model"] == "deepseek-v4-flash"
    assert isinstance(payload["max_tokens"], int)
    assert payload["max_tokens"] > 0
    assert isinstance(payload["system"], str)
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "user"
    assert isinstance(payload["messages"][0]["content"], str)
    assert "strong_rest_reminder" in payload["messages"][0]["content"]
    for value in asdict(privacy_context).values():
        assert str(value) in payload["messages"][0]["content"]


def test_payload_is_built_only_from_privacy_context_and_speech_intent(
    monkeypatch,
    privacy_context,
):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    transport = FakeTransport()

    provider = provider_class(transport=transport)
    provider.generate_companion_line(
        context=privacy_context,
        speech_intent="welcome_back",
    )

    payload_json = json.dumps(transport.calls[0]["payload"], ensure_ascii=False)
    assert "welcome_back" in payload_json
    for field_name in FORBIDDEN_FIELD_NAMES:
        assert field_name not in payload_json
    for forbidden_value in FORBIDDEN_VALUES:
        assert forbidden_value not in payload_json


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"content": []},
        {"content": [{"type": "text", "text": ""}]},
        {"content": [{"type": "text", "text": "too long " * 20}]},
    ],
)
def test_empty_or_overlong_responses_return_none(monkeypatch, privacy_context, response):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = provider_class(transport=FakeTransport(response=response))

    line = provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    assert line is None


def test_transport_exceptions_return_none_instead_of_reaching_ui(
    monkeypatch,
    privacy_context,
):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = provider_class(transport=FakeTransport(exc=TimeoutError("network down")))

    line = provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
    )

    assert line is None


def test_normal_response_parses_anthropic_content_text(monkeypatch, privacy_context):
    provider_class = _provider_class()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = provider_class(
        transport=FakeTransport(
            response={"content": [{"type": "text", "text": "stretch now"}]}
        )
    )

    line = provider.generate_companion_line(
        context=privacy_context,
        speech_intent="rest_reminder",
        timeout_seconds=3,
    )

    assert line == "stretch now"
