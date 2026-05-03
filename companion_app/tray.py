from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPixmap, QIcon, QAction, QPen, QPolygon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from companion_app.animation.actions import ACTIONS

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QWidget

logger = logging.getLogger(__name__)


def _build_tray_icon_pixmap(size: int = 32) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))

    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    outline = QColor(20, 20, 20)
    fur = QColor(35, 37, 40)
    muzzle = QColor(250, 247, 239)
    pink = QColor(245, 142, 154)

    pen = QPen(outline, 2)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(QBrush(fur))
    p.drawEllipse(6, 8, 20, 18)
    p.drawPolygon(QPolygon([QPoint(8, 12), QPoint(10, 3), QPoint(15, 11)]))
    p.drawPolygon(QPolygon([QPoint(17, 11), QPoint(22, 3), QPoint(24, 12)]))

    p.setBrush(QBrush(muzzle))
    p.drawEllipse(11, 16, 10, 7)

    p.setBrush(QBrush(pink))
    p.drawEllipse(15, 17, 3, 2)

    p.setBrush(QBrush(QColor(255, 255, 255)))
    p.drawEllipse(11, 13, 4, 4)
    p.drawEllipse(19, 13, 4, 4)

    p.setBrush(QBrush(outline))
    p.drawEllipse(12, 14, 2, 2)
    p.drawEllipse(20, 14, 2, 2)

    p.end()
    return pm


def setup_tray(
    app: QApplication,
    pet_window: QWidget,
    *,
    config: dict | None = None,
    config_path: Path | None = None,
    on_config_saved: Callable[[dict], None] | None = None,
    on_action_requested: Callable[[str], None] | None = None,
) -> QSystemTrayIcon:
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon(_build_tray_icon_pixmap()))
    tray.setToolTip("桌面宠物")

    menu = QMenu(pet_window)

    toggle_action = QAction("显示/隐藏宠物", menu)
    toggle_action.triggered.connect(lambda: pet_window.setVisible(not pet_window.isVisible()))
    menu.addAction(toggle_action)

    menu.addSeparator()

    settings_action = QAction("设置", menu)
    if config is None or config_path is None:
        settings_action.setEnabled(False)
    else:
        settings_action.triggered.connect(
            lambda: _show_settings_dialog(pet_window, config, config_path, on_config_saved)
        )
    menu.addAction(settings_action)

    if on_action_requested is not None:
        _add_action_test_menu(menu, on_action_requested)

    menu.addSeparator()

    quit_action = QAction("退出", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: _handle_tray_activation(
            reason,
            pet_window,
            config,
            config_path,
            on_config_saved,
        )
    )
    tray.show()
    tray._companion_menu = menu

    logger.info("System tray icon created.")
    return tray


def _handle_tray_activation(
    reason: QSystemTrayIcon.ActivationReason,
    parent: QWidget,
    config: dict | None,
    config_path: Path | None,
    on_config_saved: Callable[[dict], None] | None = None,
) -> None:
    if reason not in {
        QSystemTrayIcon.ActivationReason.Trigger,
        QSystemTrayIcon.ActivationReason.DoubleClick,
    }:
        return
    if config is None or config_path is None:
        return
    _show_settings_dialog(parent, config, config_path, on_config_saved)


def _add_action_test_menu(
    menu: QMenu,
    on_action_requested: Callable[[str], None],
) -> QMenu:
    action_menu = QMenu("动作测试", menu)
    menu.addMenu(action_menu)
    for action_id in ACTIONS:
        action = QAction(action_id, action_menu)
        action.setData(action_id)
        action.triggered.connect(
            lambda _checked=False, requested_action=action_id: on_action_requested(requested_action)
        )
        action_menu.addAction(action)
    menu._action_test_menu = action_menu
    return action_menu


def _show_settings_dialog(
    parent: QWidget,
    config: dict,
    config_path: Path,
    on_config_saved: Callable[[dict], None] | None = None,
) -> None:
    from companion_app.settings_window import SettingsDialog

    dialog = SettingsDialog(
        config=config,
        config_path=config_path,
        on_saved=on_config_saved,
        parent=parent,
    )
    parent._settings_dialog = dialog
    dialog.show()
