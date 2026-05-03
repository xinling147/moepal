from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtGui import QPainter, QColor, QBrush, QPixmap, QIcon, QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QWidget

logger = logging.getLogger(__name__)


def _build_tray_icon_pixmap(size: int = 32) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))

    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    # Simple round dog-face icon
    p.setBrush(QBrush(QColor(200, 160, 100)))
    p.setPen(QColor(80, 60, 40))
    p.drawEllipse(4, 6, 24, 22)

    # ears
    p.setBrush(QBrush(QColor(180, 130, 70)))
    p.drawEllipse(5, 2, 8, 10)
    p.drawEllipse(19, 2, 8, 10)

    # eyes
    p.setBrush(QBrush(QColor(30, 20, 10)))
    p.drawEllipse(12, 14, 3, 3)
    p.drawEllipse(21, 14, 3, 3)

    # nose
    p.setBrush(QBrush(QColor(40, 20, 10)))
    p.drawEllipse(16, 17, 3, 3)

    p.end()
    return pm


def setup_tray(app: QApplication, pet_window: QWidget) -> QSystemTrayIcon:
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon(_build_tray_icon_pixmap()))
    tray.setToolTip("桌面宠物")

    menu = QMenu()

    toggle_action = QAction("显示/隐藏宠物")
    toggle_action.triggered.connect(lambda: pet_window.setVisible(not pet_window.isVisible()))
    menu.addAction(toggle_action)

    menu.addSeparator()

    settings_action = QAction("设置")
    settings_action.setEnabled(False)
    menu.addAction(settings_action)

    menu.addSeparator()

    quit_action = QAction("退出")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.show()

    logger.info("System tray icon created.")
    return tray
