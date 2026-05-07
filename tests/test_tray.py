from pathlib import Path

from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget


def _app():
    app = QApplication.instance()
    return app or QApplication([])


def test_handle_tray_activation_opens_settings_on_left_click(monkeypatch, tmp_path):
    _app()
    calls = []

    def fake_show_settings(parent, config, config_path, on_config_saved=None):
        calls.append((parent, config, config_path, on_config_saved))

    monkeypatch.setattr("companion_app.tray._show_settings_dialog", fake_show_settings)

    from companion_app.tray import _handle_tray_activation

    parent = object()
    config = {"ai_enabled": False}
    config_path = tmp_path / "config.json"
    callback = lambda _config: None

    _handle_tray_activation(
        QSystemTrayIcon.ActivationReason.Trigger,
        parent,
        config,
        config_path,
        callback,
    )

    assert calls == [(parent, config, config_path, callback)]


def test_action_test_item_adds_menu_entry_and_opens_dialog(monkeypatch):
    _app()
    calls = []

    def fake_show_dialog(parent, on_action_triggered):
        calls.append(("show", parent, on_action_triggered))

    monkeypatch.setattr(
        "companion_app.tray._show_action_test_dialog", fake_show_dialog
    )

    from companion_app.tray import _add_action_test_item

    menu = QMenu()
    parent = QWidget()
    _add_action_test_item(menu, lambda aid: None, parent)

    action_texts = [a.text() for a in menu.actions()]
    assert "动作测试" in action_texts

    action_item = next(a for a in menu.actions() if a.text() == "动作测试")
    action_item.trigger()

    assert len(calls) == 1
    assert calls[0][0] == "show"


def test_setup_tray_context_menu_has_action_test_item(tmp_path):
    _app()

    from companion_app.tray import setup_tray

    window = QWidget()
    tray = setup_tray(
        _app(),
        window,
        config={"ai_enabled": False},
        config_path=tmp_path / "config.json",
        on_action_triggered=lambda _action_id: None,
    )

    menu = tray.contextMenu()
    top_level_texts = [action.text() for action in menu.actions()]

    assert "显示/隐藏宠物" in top_level_texts
    assert "设置" in top_level_texts
    assert "动作测试" in top_level_texts
    assert "退出" in top_level_texts
