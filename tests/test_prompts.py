from dataclasses import dataclass


@dataclass(frozen=True)
class PrivacyContextStub:
    active_minutes: int
    idle_minutes: int
    returned_from_idle_minutes: int | None
    time_bucket: str
    personality: str
    mood: str
    action_id: str
    app_name: str = "secret app"
    window_title: str = "secret title"
    file_path: str = "C:/Users/example/private.txt"
    keyboard_input: str = "typed secret"


FORBIDDEN = {
    "app_name",
    "window_title",
    "file_path",
    "file_name",
    "keyboard_input",
    "browser_content",
    "chat_content",
    "screenshot",
    "secret app",
    "secret title",
    "private.txt",
    "typed secret",
}


def test_build_user_prompt_uses_only_privacy_summary_fields():
    from companion_app.ai.prompts import build_user_prompt

    context = PrivacyContextStub(
        active_minutes=52,
        idle_minutes=0,
        returned_from_idle_minutes=18,
        time_bucket="late_night",
        personality="gentle",
        mood="concerned",
        action_id="concerned",
    )

    prompt = build_user_prompt(context, "late_night_care")

    assert "52" in prompt
    assert "18" in prompt
    assert "late_night" in prompt
    assert "gentle" in prompt
    assert "concerned" in prompt
    assert "late_night_care" in prompt
    assert all(forbidden not in prompt for forbidden in FORBIDDEN)


def test_build_system_prompt_sets_short_low_disturbance_boundary():
    from companion_app.ai.prompts import build_system_prompt

    prompt = build_system_prompt()

    assert "28" in prompt
    assert "应用" in prompt
    assert "文件" in prompt
    assert "窗口" in prompt


def test_sanitize_companion_line_trims_quotes_newlines_and_length():
    from companion_app.ai.prompts import sanitize_companion_line

    text = '"已经很晚了，我陪你，但也想你早点休息。\\n第二句不要出现"'

    line = sanitize_companion_line(text)

    assert line == "已经很晚了，我陪你，但也想你早点休息。"
    assert len(line) <= 28


def test_sanitize_companion_line_returns_none_for_empty_text():
    from companion_app.ai.prompts import sanitize_companion_line

    assert sanitize_companion_line("  \n\t  ") is None
