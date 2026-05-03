SIDE_EDGES = {"left", "right", "top"}


def choose_edge_action(
    edge: str,
    *,
    bottom_gap: int,
    near_bottom_threshold: int = 64,
) -> str:
    if edge == "bottom" or bottom_gap <= near_bottom_threshold:
        return "idle_lie"
    if edge in SIDE_EDGES:
        return "peek"
    return "idle_lie"


__all__ = ["choose_edge_action"]
