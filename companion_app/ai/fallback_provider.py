from __future__ import annotations

from companion_app.ai.prompts import sanitize_companion_line


class FallbackLineProvider:
    """Generate local companion lines without environment or network access."""

    _LINES = {
        "welcome_back": "你回来啦，我一直在这。",
        "soft_checkin": "我在旁边，慢慢来。",
        "rest_reminder": "要不要轻轻伸个懒腰？",
        "strong_rest_reminder": "我有点担心你，歇一会儿吧。",
        "late_night_care": "夜深了，我陪你慢慢收尾。",
    }
    _SAFE_LINE = "我在这里陪你。"

    def generate_companion_line(
        self,
        context,
        speech_intent: str,
        timeout_seconds: int = 8,
    ) -> str:
        del context, timeout_seconds
        return sanitize_companion_line(
            self._LINES.get(speech_intent, self._SAFE_LINE),
        ) or self._SAFE_LINE


__all__ = ["FallbackLineProvider"]
