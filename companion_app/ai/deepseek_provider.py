from __future__ import annotations

import json as json_module
import logging
import os
from typing import Any
from urllib import request

from companion_app.ai.prompts import (
    MAX_COMPANION_LINE_CHARS,
    build_system_prompt,
    build_user_prompt,
    sanitize_companion_line,
)
from companion_app.privacy import PrivacyContext

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.deepseek.com/anthropic"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_MAX_TOKENS = 160
DEFAULT_TIMEOUT_SECONDS = 8


class ProviderConfigurationError(RuntimeError):
    pass


class UrllibJSONTransport:
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: int,
    ) -> dict[str, Any]:
        body = json_module.dumps(json).encode("utf-8")
        req = request.Request(url, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
        return json_module.loads(response_body)


class DeepSeekAnthropicProvider:
    def __init__(
        self,
        *,
        transport: Any | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._transport = transport or UrllibJSONTransport()
        self._model = model
        self._base_url = base_url
        self._max_tokens = max_tokens
        self._timeout_seconds = timeout_seconds

    def generate_companion_line(
        self,
        context: PrivacyContext,
        speech_intent: str,
        timeout_seconds: int | None = None,
    ) -> str | None:
        api_key = self._read_api_key()
        if api_key is None:
            logger.info("DeepSeek API key is missing; falling back to local copy.")
            return None

        payload = self._build_payload(context, speech_intent)
        headers = {
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        timeout = timeout_seconds if timeout_seconds is not None else self._timeout_seconds

        try:
            response = self._transport.post(
                self._messages_url(),
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except Exception as exc:
            logger.warning("DeepSeek request failed; falling back locally: %s", exc)
            return None

        return self._parse_response_text(response)

    def _build_payload(
        self,
        context: PrivacyContext,
        speech_intent: str,
    ) -> dict[str, Any]:
        return {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "thinking": {"type": "disabled"},
            "system": build_system_prompt(),
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(context, speech_intent),
                }
            ],
        }

    def _messages_url(self) -> str:
        base_url = self._base_url or os.environ.get("ANTHROPIC_BASE_URL") or DEFAULT_BASE_URL
        return f"{base_url.rstrip('/')}/v1/messages"

    @staticmethod
    def _read_api_key() -> str | None:
        return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")

    @staticmethod
    def _parse_response_text(response: dict[str, Any]) -> str | None:
        content = response.get("content")
        if not isinstance(content, list):
            return None

        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "text":
                continue
            raw_text = item.get("text")
            if not isinstance(raw_text, str):
                continue

            lines = raw_text.replace("\\n", "\n").splitlines()
            if not lines:
                return None
            first_line = lines[0].strip()
            first_line = first_line.strip("\"'“”‘’").strip()
            if not first_line or len(first_line) > MAX_COMPANION_LINE_CHARS:
                return None
            return sanitize_companion_line(first_line)

        return None


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "DeepSeekAnthropicProvider",
    "ProviderConfigurationError",
    "UrllibJSONTransport",
]
