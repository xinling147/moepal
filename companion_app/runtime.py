from __future__ import annotations

from typing import Any

from companion_app.ai.async_provider import AsyncSpeechProvider
from companion_app.ai.deepseek_provider import DeepSeekAnthropicProvider
from companion_app.ai.fallback_provider import FallbackLineProvider
from companion_app.ai.provider import AIProvider, FallbackOnNoneProvider


def build_speech_provider(config: dict[str, Any]) -> AIProvider:
    fallback = FallbackLineProvider()

    if not config.get("ai_enabled", False):
        return fallback

    if config.get("ai_provider") != "deepseek":
        return fallback

    return FallbackOnNoneProvider(
        primary=DeepSeekAnthropicProvider(),
        fallback=fallback,
    )


def build_async_speech_provider(config: dict[str, Any], on_line) -> AIProvider:
    fallback = FallbackLineProvider()

    if not config.get("ai_enabled", False):
        return fallback

    if config.get("ai_provider") != "deepseek":
        return fallback

    return AsyncSpeechProvider(
        primary=DeepSeekAnthropicProvider(),
        fallback=fallback,
        on_line=on_line,
    )


__all__ = ["build_async_speech_provider", "build_speech_provider"]
