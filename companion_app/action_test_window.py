from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from companion_app.animation.actions import ACTIONS


class ActionTestDialog(QDialog):
    def __init__(
        self,
        *,
        on_action_triggered: Callable[[str], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._on_action_triggered = on_action_triggered

        self.setWindowTitle("动作测试")
        self.setMinimumWidth(280)

        layout = QVBoxLayout()

        header = QLabel("点击按钮测试宠物动作")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for action_id in ACTIONS:
            button = QPushButton(action_id)
            button.clicked.connect(
                lambda _checked=False, aid=action_id: self._on_action_triggered(aid)
            )
            scroll_layout.addWidget(button)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.reject)
        layout.addWidget(close_button)

        self.setLayout(layout)


__all__ = ["ActionTestDialog"]
