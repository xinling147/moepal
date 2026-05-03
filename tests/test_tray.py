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


def test_add_action_test_menu_wires_every_action():
    _app()
    triggered = []
    menu = QMenu()

    from companion_app.animation.actions import ACTIONS
    from companion_app.tray import _add_action_test_menu

    action_menu = _add_action_test_menu(menu, triggered.append)
    actions_by_id = {
        action.data(): action
        for action in action_menu.actions()
        if action.data()
    }

    assert set(actions_by_id) == set(ACTIONS)

    actions_by_id["happy_bounce"].trigger()

    assert triggered == ["happy_bounce"]


def test_setup_tray_context_menu_keeps_actions_alive(tmp_path):
    _app()

    from companion_app.animation.actions import ACTIONS
    from companion_app.tray import setup_tray

    window = QWidget()
    tray = setup_tray(
        _app(),
        window,
        config={"ai_enabled": False},
        config_path=tmp_path / "config.json",
        on_action_requested=lambda _action_id: None,
    )

    menu = tray.contextMenu()
    top_level_texts = [action.text() for action in menu.actions()]

    assert "显示/隐藏宠物" in top_level_texts
    assert "设置" in top_level_texts
    assert "动作测试" in top_level_texts
    assert "退出" in top_level_texts

    action_menu = next(
        action.menu()
        for action in menu.actions()
        if action.text() == "动作测试"
    )

    assert len(action_menu.actions()) == len(ACTIONS)
