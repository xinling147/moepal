from __future__ import annotations

import logging
from typing import Protocol

from companion_app.privacy import PrivacyContext

logger = logging.getLogger(__name__)


class AIProvider(Protocol):
    def generate_companion_line(
        self,
        context: PrivacyContext,
        speech_intent: str,
        timeout_seconds: int = 8,
    ) -> str | None:
        ...


class FallbackOnNoneProvider:
    def __init__(self, primary: AIProvider, fallback: AIProvider) -> None:
        self._primary = primary
        self._fallback = fallback

    def generate_companion_line(
        self,
        context: PrivacyContext,
        speech_intent: str,
        timeout_seconds: int = 8,
    ) -> str | None:
        try:
            line = self._primary.generate_companion_line(
                context,
                speech_intent,
                timeout_seconds,
            )
        except Exception as exc:
            logger.warning("Primary speech provider failed: %s", exc)
            line = None

        if line:
            return line
        return self._fallback.generate_companion_line(
            context,
            speech_intent,
            timeout_seconds,
        )


__all__ = ["AIProvider", "FallbackOnNoneProvider"]
