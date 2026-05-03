"""Local AI-adjacent providers for companion speech."""

from companion_app.ai.async_provider import AsyncSpeechProvider
from companion_app.ai.deepseek_provider import DeepSeekAnthropicProvider
from companion_app.ai.fallback_provider import FallbackLineProvider
from companion_app.ai.provider import AIProvider, FallbackOnNoneProvider

__all__ = [
    "AIProvider",
    "AsyncSpeechProvider",
    "DeepSeekAnthropicProvider",
    "FallbackLineProvider",
    "FallbackOnNoneProvider",
]
