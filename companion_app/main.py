from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QTimer, QObject, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QIcon, QPolygon
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSizePolicy

from companion_app.core.edge_snap import (
    CAT_EDGE_ANCHOR,
    Rect,
    Size,
    compute_edge_position,
    compute_resized_edge_position,
)
from companion_app.platform.windows_topmost import ensure_window_topmost


class PetWindow(QWidget):
    edge_changed = Signal(str, int)
    pet_clicked = Signal()
    pet_hovered = Signal()
    pet_teased = Signal()

    def __init__(self, pet_size: int = 128):
        super().__init__()
        self._pet_size = pet_size
        self._drag_offset: QPoint | None = None
        self._drag_start_pos: QPoint | None = None
        self._dragging = False
        self._attached_edge = "bottom"
        self._reanchor_on_resize = False

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # -- Speech bubble -------------------------------------------------------
        self._bubble_label = QLabel()
        self._bubble_label.setWordWrap(True)
        self._bubble_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self._bubble_label.setStyleSheet(
            "background: #ffffff;"
            "border: 1px solid #d0d0d0;"
            "border-radius: 10px;"
            "padding: 6px 10px;"
            "color: #333333;"
            "font-size: 13px;"
        )
        self._bubble_label.setVisible(False)
        self._bubble_timer: QTimer | None = None
        layout.addWidget(self._bubble_label, alignment=Qt.AlignHCenter)

        # -- Pet label -----------------------------------------------------------
        self._pet_label = QLabel()
        self._pet_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self._pet_label.setFixedSize(pet_size, pet_size)
        placeholder_pm = self._build_placeholder_pixmap(pet_size)
        self._pet_label.setPixmap(placeholder_pm)
        layout.addWidget(self._pet_label, alignment=Qt.AlignHCenter)

        self.setLayout(layout)
        self._adjust_window_size()

        self.move_to_default_position()
        self._reanchor_on_resize = True

    def _adjust_window_size(self) -> None:
        """Resize window to fit current content."""
        w = self._pet_size
        h = self._pet_size
        if self._bubble_label.isVisible():
            w = max(w, self._bubble_label.sizeHint().width())
            h += self._bubble_label.sizeHint().height() + 4
        self.setFixedSize(w, h)
        self._reanchor_to_attached_edge()
        self._enforce_topmost()

    def _reanchor_to_attached_edge(self) -> None:
        if not self._reanchor_on_resize:
            return

        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        if screen is None:
            return

        geom = screen.availableGeometry()
        current = self.frameGeometry()
        new_x, new_y = compute_resized_edge_position(
            self._attached_edge,
            Rect(geom.left(), geom.top(), geom.right(), geom.bottom()),
            Size(self.width(), self.height()),
            current_left=current.left(),
            current_top=current.top(),
            anchor=CAT_EDGE_ANCHOR,
        )
        self.move(new_x, new_y)

    def _enforce_topmost(self) -> None:
        ensure_window_topmost(self)

    # -- Dev-spec public API ----------------------------------------------------

    def set_frame(self, pixmap: QPixmap) -> None:
        """Display *pixmap* as the current pet frame."""
        if pixmap.isNull():
            return

        scaled = pixmap.scaled(
            self._pet_size, self._pet_size,
            Qt.KeepAspectRatio, Qt.SmoothTransformation,
        )
        self._pet_label.setPixmap(scaled)

    def show_bubble(self, text: str, ttl_ms: int = 6000) -> None:
        """Show a speech bubble with text for ttl_ms milliseconds."""
        self._bubble_label.setText(text)
        self._bubble_label.setVisible(True)
        self._adjust_window_size()

        if self._bubble_timer is not None:
            self._bubble_timer.stop()
        self._bubble_timer = QTimer(self)
        self._bubble_timer.setSingleShot(True)
        self._bubble_timer.timeout.connect(self._hide_bubble)
        self._bubble_timer.start(ttl_ms)

    def _hide_bubble(self) -> None:
        self._bubble_label.setVisible(False)
        self._adjust_window_size()
        self._bubble_timer = None

    def move_to_default_position(self) -> None:
        """Place window at the bottom-right corner of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is not None:
            geom = screen.availableGeometry()
            x, y = compute_edge_position(
                "bottom",
                Rect(geom.left(), geom.top(), geom.right(), geom.bottom()),
                Size(self.width(), self.height()),
                current_left=geom.right() - self.width() + 1,
                current_top=geom.bottom() - self.height() + 1,
                anchor=CAT_EDGE_ANCHOR,
            )
            self.move(max(0, x), max(0, y))
            self._set_attached_edge("bottom")
            self._enforce_topmost()

    def snap_to_nearest_edge(self, margin: int = 0) -> None:
        """Snap the window to the nearest screen edge (left / right / top / bottom)."""
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        if screen is None:
            return

        geom = screen.availableGeometry()
        current = self.frameGeometry()

        distances = {
            "left": abs(current.left() - geom.left()),
            "right": abs(geom.right() - current.right()),
            "top": abs(current.top() - geom.top()),
            "bottom": abs(geom.bottom() - current.bottom()),
        }
        edge = min(distances, key=distances.get)

        new_x, new_y = compute_edge_position(
            edge,
            Rect(geom.left(), geom.top(), geom.right(), geom.bottom()),
            Size(self.width(), self.height()),
            current_left=current.left(),
            current_top=current.top(),
            margin=margin,
            anchor=CAT_EDGE_ANCHOR,
        )
        self.move(new_x, new_y)
        self._set_attached_edge(edge)
        self._enforce_topmost()
        self.edge_changed.emit(edge, self._bottom_gap(geom))

    def _set_attached_edge(self, edge: str) -> None:
        self._attached_edge = edge
        if edge == "left":
            alignment = Qt.AlignLeft | Qt.AlignVCenter
        elif edge == "right":
            alignment = Qt.AlignRight | Qt.AlignVCenter
        elif edge == "top":
            alignment = Qt.AlignHCenter | Qt.AlignTop
        else:
            alignment = Qt.AlignHCenter | Qt.AlignBottom
        self._pet_label.setAlignment(alignment)

    def _bottom_gap(self, geom) -> int:
        return max(0, geom.bottom() - self.frameGeometry().bottom())

    # -- Backwards-compatible alias ---------------------------------------------

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.set_frame(pixmap)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._enforce_topmost()

    # -- Placeholder drawing ----------------------------------------------------

    @staticmethod
    def _build_placeholder_pixmap(size: int) -> QPixmap:
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)

        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)

        outline = QColor(22, 22, 22)
        fur = QColor(34, 36, 38)
        muzzle = QColor(250, 247, 239)
        pink = QColor(245, 142, 154)

        p.setPen(QPen(outline, max(2, size // 42), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QBrush(fur))

        head_rect = (int(size * 0.25), int(size * 0.22), int(size * 0.5), int(size * 0.42))
        p.drawEllipse(*head_rect)
        p.drawPolygon(QPolygon([
            QPoint(int(size * 0.30), int(size * 0.30)),
            QPoint(int(size * 0.35), int(size * 0.12)),
            QPoint(int(size * 0.44), int(size * 0.30)),
        ]))
        p.drawPolygon(QPolygon([
            QPoint(int(size * 0.56), int(size * 0.30)),
            QPoint(int(size * 0.65), int(size * 0.12)),
            QPoint(int(size * 0.70), int(size * 0.30)),
        ]))

        p.setBrush(QBrush(muzzle))
        p.drawEllipse(int(size * 0.36), int(size * 0.42), int(size * 0.28), int(size * 0.22))
        p.drawEllipse(int(size * 0.26), int(size * 0.56), int(size * 0.18), int(size * 0.16))
        p.drawEllipse(int(size * 0.56), int(size * 0.56), int(size * 0.18), int(size * 0.16))

        p.setBrush(QBrush(pink))
        p.drawEllipse(int(size * 0.47), int(size * 0.47), int(size * 0.06), int(size * 0.04))

        p.setBrush(QBrush(outline))
        er = max(3, size // 28)
        p.drawEllipse(int(size * 0.39), int(size * 0.38), er, er)
        p.drawEllipse(int(size * 0.58), int(size * 0.38), er, er)

        p.end()
        return pm

    # -- Dragging ---------------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPosition().toPoint()
            self._drag_start_pos = global_pos
            self._drag_offset = global_pos - self.frameGeometry().topLeft()
            self._dragging = False

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        global_pos = event.globalPosition().toPoint()
        if self._drag_offset is not None and self._drag_start_pos is not None:
            if (global_pos - self._drag_start_pos).manhattanLength() >= 4:
                self._dragging = True
                self.move(global_pos - self._drag_offset)
            return

        self.pet_teased.emit()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            was_dragging = self._dragging
            self._drag_offset = None
            self._drag_start_pos = None
            self._dragging = False
            if was_dragging:
                self.snap_to_nearest_edge()
            else:
                self.pet_clicked.emit()

    def enterEvent(self, event) -> None:  # type: ignore[override]
        super().enterEvent(event)
        self.pet_hovered.emit()


class BubbleDispatcher(QObject):
    line_ready = Signal(str)

    def __init__(self, window: PetWindow):
        super().__init__(window)
        self.line_ready.connect(window.show_bubble)

    def show_line(self, text: str) -> None:
        self.line_ready.emit(text)


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    from companion_app.config import load_config
    from companion_app.paths import get_config_path, get_sprites_dir

    config_path = get_config_path()
    config = load_config(config_path)
    pet_size = int(config.get("pet_size", 128))

    window = PetWindow(pet_size)
    window.show()

    from companion_app.activity.session_tracker import SessionTracker
    from companion_app.animation.animator import Animator
    from companion_app.animation.sprites import create_frame_loader
    from companion_app.core.behavior import BehaviorEngine
    from companion_app.core.controller import CompanionController
    from companion_app.core.pet_state import PetState
    from companion_app.runtime import build_async_speech_provider, build_speech_provider

    pet_state = PetState(personality=str(config.get("personality", "gentle")))
    animator = Animator(create_frame_loader(get_sprites_dir()))
    bubble_dispatcher = BubbleDispatcher(window)
    speech_provider = (
        build_async_speech_provider(config, bubble_dispatcher.show_line)
        if config.get("ai_enabled", False)
        else build_speech_provider(config)
    )
    controller = CompanionController(
        activity_tracker=SessionTracker(),
        behavior_engine=BehaviorEngine(),
        animator=animator,
        window=window,
        speech_provider=speech_provider,
        pet_state=pet_state,
        bubble_enabled=bool(config.get("bubble_enabled", True)),
    )
    window.edge_changed.connect(controller.handle_edge_pose)
    window.pet_clicked.connect(lambda: controller.handle_user_interaction("click"))
    window.pet_hovered.connect(lambda: controller.handle_user_interaction("hover"))
    window.pet_teased.connect(lambda: controller.handle_user_interaction("tease"))

    def apply_saved_settings(updated_config: dict) -> None:
        provider = (
            build_async_speech_provider(updated_config, bubble_dispatcher.show_line)
            if updated_config.get("ai_enabled", False)
            else build_speech_provider(updated_config)
        )
        controller.apply_runtime_settings(updated_config, speech_provider=provider)

    from companion_app.tray import setup_tray
    tray = setup_tray(
        app,
        window,
        config=config,
        config_path=config_path,
        on_config_saved=apply_saved_settings,
    )

    animation_timer = QTimer(window)
    animation_timer.timeout.connect(lambda: controller.tick_animation(0.1))
    animation_timer.start(100)

    behavior_timer = QTimer(window)
    behavior_timer.timeout.connect(controller.tick_behavior)
    behavior_timer.start(5000)

    window._companion_controller = controller
    window._animation_timer = animation_timer
    window._behavior_timer = behavior_timer
    window._bubble_dispatcher = bubble_dispatcher
    window._tray = tray

    controller.tick_animation(0.0)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
