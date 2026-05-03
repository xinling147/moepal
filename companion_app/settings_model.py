from __future__ import annotations

import os
from typing import Any


def build_settings_state(config: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""
    return {
        "ai_enabled": bool(config.get("ai_enabled", False)),
        "bubble_enabled": bool(config.get("bubble_enabled", True)),
        "personality": str(config.get("personality", "gentle")),
        "pet_size": int(config.get("pet_size", 128)),
        "api_key_configured": bool(api_key),
        "api_key_display": _mask_api_key(api_key) if api_key else "未配置",
    }


def _mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "已配置"
    return f"{api_key[:4]}...{api_key[-4:]}"


__all__ = ["build_settings_state"]
