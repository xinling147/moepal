from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QPainter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAT_SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites" / "cat"


@dataclass(frozen=True)
class FrameTransform:
    dx: int = 0
    dy: int = 0
    scale_x: float = 1.0
    scale_y: float = 1.0
    mirror: bool = False


ACTION_SOURCES = {
    "idle_lie": "idle_lie",
    "sleep": "sleep",
    "peek": "peek",
    "nudge": "nudge",
    "tail_wag": "idle_lie",
    "happy_bounce": "idle_lie",
    "look_around": "peek",
    "sit_wait": "idle_lie",
}


ACTION_TRANSFORMS = {
    "idle_lie": [
        FrameTransform(dy=0),
        FrameTransform(dy=-1),
        FrameTransform(dy=-2, scale_y=1.01),
        FrameTransform(dy=-1),
        FrameTransform(dy=0),
        FrameTransform(dy=1),
        FrameTransform(dy=2, scale_y=0.99),
        FrameTransform(dy=1),
    ],
    "sleep": [
        FrameTransform(dy=0),
        FrameTransform(dy=1, scale_y=0.995),
        FrameTransform(dy=2, scale_y=0.99),
        FrameTransform(dy=1, scale_y=0.995),
        FrameTransform(dy=0),
        FrameTransform(dy=-1, scale_y=1.005),
    ],
    "peek": [
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=-2, dy=-1),
        FrameTransform(dx=-3, dy=-2),
        FrameTransform(dx=-2, dy=-1),
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=2, dy=0),
        FrameTransform(dx=3, dy=1),
        FrameTransform(dx=2, dy=0),
    ],
    "nudge": [
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=-3, dy=-1),
        FrameTransform(dx=-6, dy=-1),
        FrameTransform(dx=-3, dy=0),
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=2, dy=1),
        FrameTransform(dx=4, dy=1),
        FrameTransform(dx=2, dy=0),
    ],
    "tail_wag": [
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=1, dy=-1),
        FrameTransform(dx=2, dy=0),
        FrameTransform(dx=1, dy=1),
        FrameTransform(dx=0, dy=0),
        FrameTransform(dx=-1, dy=-1),
        FrameTransform(dx=-2, dy=0),
        FrameTransform(dx=-1, dy=1),
    ],
    "happy_bounce": [
        FrameTransform(dy=0),
        FrameTransform(dy=-4, scale_y=1.01),
        FrameTransform(dy=-8, scale_y=1.02),
        FrameTransform(dy=-4, scale_y=1.01),
        FrameTransform(dy=0),
        FrameTransform(dy=2, scale_y=0.985),
        FrameTransform(dy=0),
        FrameTransform(dy=-2),
    ],
    "look_around": [
        FrameTransform(dx=0),
        FrameTransform(dx=-3),
        FrameTransform(dx=0),
        FrameTransform(dx=3),
        FrameTransform(dx=0),
        FrameTransform(dx=4),
    ],
    "sit_wait": [
        FrameTransform(dy=0),
        FrameTransform(dy=-1),
        FrameTransform(dy=0),
        FrameTransform(dy=1),
        FrameTransform(dy=0),
        FrameTransform(dy=-1, scale_y=1.005),
    ],
}


def main() -> None:
    for action_id, transforms in ACTION_TRANSFORMS.items():
        source = _load_source(ACTION_SOURCES[action_id])
        action_dir = CAT_SPRITES_DIR / action_id
        action_dir.mkdir(parents=True, exist_ok=True)

        for frame_index, transform in enumerate(transforms):
            frame = _render_frame(source, transform)
            output_path = action_dir / f"frame_{frame_index:03d}.png"
            if not frame.save(str(output_path), "PNG"):
                raise RuntimeError(f"Failed to save {output_path}")


def _load_source(action_id: str) -> QImage:
    source_path = CAT_SPRITES_DIR / action_id / "frame_000.png"
    image = QImage(str(source_path))
    if image.isNull():
        raise FileNotFoundError(source_path)
    return image.convertToFormat(QImage.Format.Format_ARGB32)


def _render_frame(source: QImage, transform: FrameTransform) -> QImage:
    source_image = source.mirrored(True, False) if transform.mirror else source
    frame = QImage(source.width(), source.height(), QImage.Format.Format_ARGB32)
    frame.fill(0)

    target_width = max(1, round(source.width() * transform.scale_x))
    target_height = max(1, round(source.height() * transform.scale_y))
    target_x = (source.width() - target_width) // 2 + transform.dx
    target_y = (source.height() - target_height) // 2 + transform.dy

    painter = QPainter(frame)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawImage(
        QRect(target_x, target_y, target_width, target_height),
        source_image,
        source_image.rect(),
    )
    painter.end()

    return frame


if __name__ == "__main__":
    main()
