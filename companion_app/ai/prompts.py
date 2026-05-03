from __future__ import annotations

from typing import Any

MAX_COMPANION_LINE_CHARS = 28


def build_system_prompt() -> str:
    return (
        "你是一只温柔、低打扰的桌面像素狗。"
        "只回复一句中文短句，不超过28个字符。"
        "不要命令或责备用户。"
        "不要提到具体应用、窗口、文件、网页、输入内容或截图。"
    )


def build_user_prompt(context: Any, speech_intent: str) -> str:
    returned = getattr(context, "returned_from_idle_minutes")
    returned_text = "无" if returned is None else f"{returned}分钟"
    return "\n".join(
        [
            f"speech_intent: {speech_intent}",
            f"active_minutes: {getattr(context, 'active_minutes')}",
            f"idle_minutes: {getattr(context, 'idle_minutes')}",
            f"returned_from_idle_minutes: {returned_text}",
            f"time_bucket: {getattr(context, 'time_bucket')}",
            f"personality: {getattr(context, 'personality')}",
            f"mood: {getattr(context, 'mood')}",
            f"action_id: {getattr(context, 'action_id')}",
        ]
    )


def sanitize_companion_line(
    text: str | None,
    max_chars: int = MAX_COMPANION_LINE_CHARS,
) -> str | None:
    if text is None:
        return None

    line = str(text).strip()
    if not line:
        return None

    line = line.replace("\\n", "\n")
    line = line.splitlines()[0].strip()
    line = line.strip("\"'“”‘’")
    line = line.strip()
    if not line:
        return None

    if len(line) > max_chars:
        return line[:max_chars]
    return line


__all__ = [
    "MAX_COMPANION_LINE_CHARS",
    "build_system_prompt",
    "build_user_prompt",
    "sanitize_companion_line",
]
