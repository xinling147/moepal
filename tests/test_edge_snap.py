from companion_app.core import edge_snap
from companion_app.core.edge_snap import (
    CAT_EDGE_ANCHOR,
    EdgeAnchor,
    Rect,
    Size,
    compute_edge_position,
)


def _compute_resized_edge_position(*args, **kwargs):
    fn = getattr(edge_snap, "compute_resized_edge_position", None)
    assert callable(fn), "compute_resized_edge_position should handle edge re-anchoring after resize"
    return fn(*args, **kwargs)


def test_bottom_anchor_aligns_internal_surface_to_screen_bottom():
    screen = Rect(left=0, top=0, right=1919, bottom=899)
    window = Size(width=128, height=128)

    x, y = compute_edge_position(
        "bottom",
        screen,
        window,
        current_left=1600,
        current_top=700,
        anchor=EdgeAnchor(bottom=0.625),
    )

    assert x == 1600
    assert y == 820


def test_right_anchor_allows_pet_to_peek_from_screen_edge():
    screen = Rect(left=0, top=0, right=1919, bottom=899)
    window = Size(width=128, height=128)

    x, y = compute_edge_position(
        "right",
        screen,
        window,
        current_left=1700,
        current_top=300,
        anchor=EdgeAnchor(right=0.75),
    )

    assert x == 1824
    assert y == 300


def test_perpendicular_axis_is_clamped_when_anchor_overhangs():
    screen = Rect(left=0, top=0, right=1919, bottom=899)
    window = Size(width=128, height=128)

    x, y = compute_edge_position(
        "bottom",
        screen,
        window,
        current_left=1900,
        current_top=700,
        anchor=EdgeAnchor(bottom=0.625),
    )

    assert x == 1792
    assert y == 820


def test_default_cat_bottom_anchor_keeps_sprite_above_taskbar_area():
    screen = Rect(left=0, top=0, right=1919, bottom=899)
    window = Size(width=128, height=128)

    x, y = compute_edge_position(
        "bottom",
        screen,
        window,
        current_left=1600,
        current_top=700,
        anchor=CAT_EDGE_ANCHOR,
    )

    assert x == 1600
    assert y == 772


def test_resized_bottom_anchor_stays_on_available_bottom_when_height_grows_and_shrinks():
    screen = Rect(left=0, top=0, right=1919, bottom=899)

    grown_x, grown_y = _compute_resized_edge_position(
        "bottom",
        screen,
        Size(width=160, height=200),
        current_left=1700,
        current_top=772,
    )
    shrunk_x, shrunk_y = _compute_resized_edge_position(
        "bottom",
        screen,
        Size(width=128, height=96),
        current_left=1700,
        current_top=grown_y,
    )

    assert grown_x == 1700
    assert grown_y + 200 - 1 == screen.bottom
    assert shrunk_x == 1700
    assert shrunk_y + 96 - 1 == screen.bottom


def test_resized_right_and_left_anchors_stay_on_available_edge_when_width_changes():
    screen = Rect(left=10, top=20, right=1009, bottom=819)

    right_x, right_y = _compute_resized_edge_position(
        "right",
        screen,
        Size(width=200, height=128),
        current_left=850,
        current_top=500,
        anchor=CAT_EDGE_ANCHOR,
    )
    left_x, left_y = _compute_resized_edge_position(
        "left",
        screen,
        Size(width=96, height=128),
        current_left=10,
        current_top=500,
        anchor=CAT_EDGE_ANCHOR,
    )

    assert right_x == screen.right + 1 - round(200 * CAT_EDGE_ANCHOR.right)
    assert right_y == 500
    assert left_x == screen.left - round(96 * CAT_EDGE_ANCHOR.left)
    assert left_y == 500


def test_resized_edge_position_clamps_perpendicular_axis_inside_available_area():
    screen = Rect(left=10, top=20, right=1009, bottom=819)

    bottom_x, bottom_y = _compute_resized_edge_position(
        "bottom",
        screen,
        Size(width=200, height=128),
        current_left=950,
        current_top=700,
    )
    right_x, right_y = _compute_resized_edge_position(
        "right",
        screen,
        Size(width=128, height=200),
        current_left=900,
        current_top=750,
    )

    assert bottom_x == 810
    assert bottom_y + 128 - 1 == screen.bottom
    assert right_x + 128 - 1 == screen.right
    assert right_y == 620
