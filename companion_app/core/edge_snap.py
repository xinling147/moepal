from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int


@dataclass(frozen=True)
class Size:
    width: int
    height: int


@dataclass(frozen=True)
class EdgeAnchor:
    left: float = 0.0
    right: float = 1.0
    top: float = 0.0
    bottom: float = 1.0


CAT_EDGE_ANCHOR = EdgeAnchor(
    left=0.25,
    right=0.75,
    top=0.0,
    bottom=1.0,
)


def clamp(value: int, minimum: int, maximum: int) -> int:
    if maximum < minimum:
        return minimum
    return max(minimum, min(value, maximum))


def compute_edge_position(
    edge: str,
    screen: Rect,
    window: Size,
    *,
    current_left: int,
    current_top: int,
    margin: int = 0,
    anchor: EdgeAnchor | None = None,
) -> tuple[int, int]:
    anchor = anchor or EdgeAnchor()

    min_x = screen.left + margin
    max_x = screen.right - window.width + 1 - margin
    min_y = screen.top + margin
    max_y = screen.bottom - window.height + 1 - margin

    x = clamp(current_left, min_x, max_x)
    y = clamp(current_top, min_y, max_y)

    if edge == "left":
        x = screen.left - round(window.width * anchor.left) + margin
    elif edge == "right":
        x = screen.right + 1 - round(window.width * anchor.right) - margin
    elif edge == "top":
        y = screen.top - round(window.height * anchor.top) + margin
    else:
        y = screen.bottom + 1 - round(window.height * anchor.bottom) - margin

    return x, y


def compute_resized_edge_position(
    edge: str,
    screen: Rect,
    window: Size,
    *,
    current_left: int,
    current_top: int,
    margin: int = 0,
    anchor: EdgeAnchor | None = None,
) -> tuple[int, int]:
    """Recompute an attached window's top-left after its size changes.

    The math intentionally stays identical to compute_edge_position: resizing
    should preserve the current attached edge and edge anchor, while reclamping
    the perpendicular axis for the new dimensions.
    """
    return compute_edge_position(
        edge,
        screen,
        window,
        current_left=current_left,
        current_top=current_top,
        margin=margin,
        anchor=anchor,
    )


__all__ = [
    "CAT_EDGE_ANCHOR",
    "EdgeAnchor",
    "Rect",
    "Size",
    "compute_edge_position",
    "compute_resized_edge_position",
]
