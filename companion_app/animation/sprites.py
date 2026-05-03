import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PLACEHOLDER_SIZE = 128


def _discover_frame_files(action_id: str, base_path: Path) -> list[Path]:
    """Return sorted PNG frame paths for *action_id*, falling back to idle_lie.

    If idle_lie itself has no frames, returns an empty list.
    This is the filesystem-logic layer — no Qt dependency.
    """
    action_dir = base_path / action_id
    if action_dir.is_dir():
        png_files = sorted(action_dir.glob("frame_*.png"))
        if png_files:
            return png_files

    if action_id != "idle_lie":
        logger.debug("No frames for '%s', falling back to idle_lie.", action_id)
        return _discover_frame_files("idle_lie", base_path)

    return []


def _find_opaque_bounds(image, alpha_threshold: int = 0):
    from PySide6.QtCore import QRect

    min_x = image.width()
    min_y = image.height()
    max_x = -1
    max_y = -1

    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y).alpha() > alpha_threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x < min_x or max_y < min_y:
        return None

    return QRect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def _is_dark_opaque(pixel, *, dark_threshold: int, alpha_threshold: int) -> bool:
    return (
        pixel.alpha() > alpha_threshold
        and pixel.red() <= dark_threshold
        and pixel.green() <= dark_threshold
        and pixel.blue() <= dark_threshold
    )


def remove_horizontal_edge_guides(
    image,
    *,
    min_coverage_ratio: float = 0.45,
    dark_threshold: int = 48,
    alpha_threshold: int = 16,
):
    """Remove long dark horizontal guide lines baked into concept sprites."""
    from PySide6.QtGui import QColor

    if image.isNull():
        return image

    cleaned = image.copy()
    width = cleaned.width()
    if width <= 0:
        return cleaned

    min_coverage = max(1, round(width * min_coverage_ratio))
    start_y = round(cleaned.height() * 0.45)

    for y in range(start_y, cleaned.height()):
        dark_pixels: list[int] = []
        longest_run = 0
        current_run = 0
        supported_dark_pixels = 0

        for x in range(width):
            if _is_dark_opaque(
                cleaned.pixelColor(x, y),
                dark_threshold=dark_threshold,
                alpha_threshold=alpha_threshold,
            ):
                dark_pixels.append(x)
                current_run += 1
                longest_run = max(longest_run, current_run)
                has_dark_above = y > 0 and _is_dark_opaque(
                    cleaned.pixelColor(x, y - 1),
                    dark_threshold=dark_threshold,
                    alpha_threshold=alpha_threshold,
                )
                has_dark_below = y < cleaned.height() - 1 and _is_dark_opaque(
                    cleaned.pixelColor(x, y + 1),
                    dark_threshold=dark_threshold,
                    alpha_threshold=alpha_threshold,
                )
                if has_dark_above or has_dark_below:
                    supported_dark_pixels += 1
            else:
                current_run = 0

        if longest_run < min_coverage:
            continue
        if dark_pixels and supported_dark_pixels / len(dark_pixels) > 0.35:
            continue

        for x in dark_pixels:
            cleaned.setPixelColor(x, y, QColor(0, 0, 0, 0))

    return cleaned


def trim_transparent_pixmap(pixmap, alpha_threshold: int = 0):
    from PySide6.QtGui import QPixmap

    if pixmap.isNull():
        return pixmap

    image = pixmap.toImage()
    bounds = _find_opaque_bounds(image, alpha_threshold)
    if bounds is None or bounds == image.rect():
        return pixmap

    return QPixmap.fromImage(image.copy(bounds))


def clean_sprite_pixmap(pixmap):
    from PySide6.QtGui import QPixmap

    if pixmap.isNull():
        return pixmap

    image = remove_horizontal_edge_guides(pixmap.toImage())
    return QPixmap.fromImage(image)


def _generate_placeholder_pixmap(size: int = PLACEHOLDER_SIZE):
    from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPolygon
    from PySide6.QtCore import Qt, QPoint

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    outline = QColor(22, 22, 22)
    fur = QColor(34, 36, 38)
    muzzle = QColor(250, 247, 239)
    pink = QColor(245, 142, 154)

    painter.setPen(QPen(outline, max(2, size // 42), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(QBrush(fur))

    head_rect = (int(size * 0.25), int(size * 0.22), int(size * 0.5), int(size * 0.42))
    painter.drawEllipse(*head_rect)
    painter.drawPolygon(QPolygon([
        QPoint(int(size * 0.30), int(size * 0.30)),
        QPoint(int(size * 0.35), int(size * 0.12)),
        QPoint(int(size * 0.44), int(size * 0.30)),
    ]))
    painter.drawPolygon(QPolygon([
        QPoint(int(size * 0.56), int(size * 0.30)),
        QPoint(int(size * 0.65), int(size * 0.12)),
        QPoint(int(size * 0.70), int(size * 0.30)),
    ]))

    painter.setBrush(QBrush(muzzle))
    painter.drawEllipse(int(size * 0.36), int(size * 0.42), int(size * 0.28), int(size * 0.22))
    painter.drawEllipse(int(size * 0.26), int(size * 0.56), int(size * 0.18), int(size * 0.16))
    painter.drawEllipse(int(size * 0.56), int(size * 0.56), int(size * 0.18), int(size * 0.16))

    painter.setBrush(QBrush(pink))
    painter.drawEllipse(int(size * 0.47), int(size * 0.47), int(size * 0.06), int(size * 0.04))

    painter.setBrush(QBrush(outline))
    eye_r = max(3, size // 28)
    painter.drawEllipse(int(size * 0.39), int(size * 0.38), eye_r, eye_r)
    painter.drawEllipse(int(size * 0.58), int(size * 0.38), eye_r, eye_r)

    painter.end()
    return pixmap


def load_frames(action_id: str, base_path: Path):
    """Load QPixmap frames for *action_id* from disk.

    Uses _discover_frame_files for path resolution.  Falls back to
    idle_lie, then to a programmatic placeholder.
    """
    from PySide6.QtGui import QPixmap

    frames: list = []
    for png_file in _discover_frame_files(action_id, base_path):
        pixmap = QPixmap(str(png_file))
        if not pixmap.isNull():
            frames.append(trim_transparent_pixmap(clean_sprite_pixmap(pixmap)))

    if not frames:
        logger.warning("No frames for idle_lie, using generated placeholder.")
        frames.append(_generate_placeholder_pixmap())

    return frames


def create_frame_loader(sprites_base_path: Path):
    """Return a FrameLoader callable suitable for Animator."""
    cache: dict[str, list] = {}

    def _loader(action_id: str):
        if action_id not in cache:
            cache[action_id] = load_frames(action_id, sprites_base_path)
        return list(cache[action_id])

    return _loader
