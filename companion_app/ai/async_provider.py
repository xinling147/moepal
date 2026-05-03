from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from companion_app.ai.provider import AIProvider
from companion_app.privacy import PrivacyContext

logger = logging.getLogger(__name__)


class AsyncSpeechProvider:
    def __init__(
        self,
        primary: AIProvider,
        fallback: AIProvider,
        on_line: Callable[[str], None],
        *,
        executor=None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._on_line = on_line
        self._executor = executor or ThreadPoolExecutor(max_workers=1)

    def generate_companion_line(
        self,
        context: PrivacyContext,
        speech_intent: str,
        timeout_seconds: int = 8,
    ) -> None:
        def _run() -> None:
            line = None
            try:
                line = self._primary.generate_companion_line(
                    context,
                    speech_intent,
                    timeout_seconds,
                )
            except Exception as exc:
                logger.warning("Async primary speech provider failed: %s", exc)

            if not line:
                try:
                    line = self._fallback.generate_companion_line(
                        context,
                        speech_intent,
                        timeout_seconds,
                    )
                except Exception as exc:
                    logger.warning("Async fallback speech provider failed: %s", exc)
                    line = None

            if line:
                self._on_line(line)

        self._executor.submit(_run)
        return None


__all__ = ["AsyncSpeechProvider"]
