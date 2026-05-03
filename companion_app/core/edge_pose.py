SIDE_EDGES = {"left", "right", "top"}


def choose_edge_action(
    edge: str,
    *,
    bottom_gap: int,
    near_bottom_threshold: int = 64,
    walk_edge_threshold: int = 240,
) -> str:
    if edge == "bottom" or bottom_gap <= near_bottom_threshold:
        return "idle_lie"
    if edge in {"left", "right"} and bottom_gap <= walk_edge_threshold:
        return "walk_edge"
    if edge in SIDE_EDGES:
        return "peek"
    return "idle_lie"


__all__ = ["choose_edge_action"]
