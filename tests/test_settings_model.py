from __future__ import annotations

from companion_app.settings_model import build_settings_state


def test_build_settings_state_masks_deepseek_api_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-1234567890abcdef")

    state = build_settings_state({"ai_enabled": True, "personality": "gentle"})

    assert state["api_key_configured"] is True
    assert state["api_key_display"] == "sk-1...cdef"


def test_build_settings_state_reports_missing_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    state = build_settings_state({"ai_enabled": False, "personality": "lively"})

    assert state["api_key_configured"] is False
    assert state["api_key_display"] == "未配置"
    assert state["personality"] == "lively"
