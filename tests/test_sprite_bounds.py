from PySide6.QtGui import QColor, QImage

from companion_app.animation.sprites import _find_opaque_bounds, remove_horizontal_edge_guides


def test_find_opaque_bounds_ignores_transparent_padding():
    image = QImage(10, 12, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))

    for y in range(4, 9):
        for x in range(3, 7):
            image.setPixelColor(x, y, QColor(10, 20, 30, 255))

    bounds = _find_opaque_bounds(image)

    assert bounds is not None
    assert (bounds.x(), bounds.y(), bounds.width(), bounds.height()) == (3, 4, 4, 5)


def test_remove_horizontal_edge_guides_makes_long_dark_guide_transparent():
    image = QImage(20, 12, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))

    for x in range(2, 18):
        image.setPixelColor(x, 8, QColor(0, 0, 0, 255))
    image.setPixelColor(6, 4, QColor(0, 0, 0, 255))

    cleaned = remove_horizontal_edge_guides(image, min_coverage_ratio=0.6)

    assert cleaned.pixelColor(10, 8).alpha() == 0
    assert cleaned.pixelColor(6, 4).alpha() == 255


def test_remove_horizontal_edge_guides_preserves_dark_fur_mass():
    image = QImage(20, 12, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))

    for y in range(5, 10):
        for x in range(2, 18):
            image.setPixelColor(x, y, QColor(18, 18, 18, 255))

    cleaned = remove_horizontal_edge_guides(image, min_coverage_ratio=0.6)

    assert cleaned.pixelColor(10, 7).alpha() == 255
