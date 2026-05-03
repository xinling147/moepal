from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from companion_app.config import save_config
from companion_app.settings_model import build_settings_state


_PERSONALITY_LABELS = {
    "gentle": "温柔陪伴型",
    "lively": "活泼撒娇型",
    "quiet": "安静守护型",
}


class SettingsDialog(QDialog):
    def __init__(
        self,
        *,
        config: dict[str, Any],
        config_path: Path,
        on_saved: Callable[[dict[str, Any]], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._config = config
        self._config_path = config_path
        self._on_saved = on_saved

        self.setWindowTitle("桌宠设置")
        self.setMinimumWidth(360)

        state = build_settings_state(config)

        self._ai_enabled = QCheckBox("启用 AI 文案")
        self._ai_enabled.setChecked(state["ai_enabled"])

        self._bubble_enabled = QCheckBox("显示气泡")
        self._bubble_enabled.setChecked(state["bubble_enabled"])

        self._personality = QComboBox()
        for key, label in _PERSONALITY_LABELS.items():
            self._personality.addItem(label, key)
        personality_index = self._personality.findData(state["personality"])
        self._personality.setCurrentIndex(max(0, personality_index))

        self._pet_size = QSpinBox()
        self._pet_size.setRange(128, 160)
        self._pet_size.setSingleStep(32)
        self._pet_size.setValue(state["pet_size"])

        self._api_key = QLineEdit()
        self._api_key.setEchoMode(QLineEdit.Password)
        self._api_key.setPlaceholderText("可选，只应用到本次运行，不写入配置文件")

        api_status = QLabel(state["api_key_display"])
        api_status.setTextInteractionFlags(api_status.textInteractionFlags())

        form = QFormLayout()
        form.addRow("", self._ai_enabled)
        form.addRow("", self._bubble_enabled)
        form.addRow("性格", self._personality)
        form.addRow("尺寸", self._pet_size)
        form.addRow("DeepSeek Key", self._api_key)
        form.addRow("Key 状态", api_status)

        save_button = QPushButton("保存")
        cancel_button = QPushButton("取消")
        save_button.clicked.connect(self._save)
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def _save(self) -> None:
        self._config["ai_enabled"] = self._ai_enabled.isChecked()
        self._config["bubble_enabled"] = self._bubble_enabled.isChecked()
        self._config["personality"] = str(self._personality.currentData())
        self._config["pet_size"] = int(self._pet_size.value())

        api_key = self._api_key.text().strip()
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key

        save_config(self._config, self._config_path)
        if self._on_saved is not None:
            self._on_saved(self._config)
        self.accept()


__all__ = ["SettingsDialog"]
