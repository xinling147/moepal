from companion_app.core.edge_pose import choose_edge_action


def test_choose_edge_action_uses_walk_edge_for_side_edge_above_bottom():
    assert choose_edge_action("right", bottom_gap=180) == "walk_edge"


def test_choose_edge_action_uses_peek_for_high_side_edge():
    assert choose_edge_action("right", bottom_gap=320) == "peek"


def test_choose_edge_action_uses_peek_for_top_edge():
    assert choose_edge_action("top", bottom_gap=320) == "peek"


def test_choose_edge_action_keeps_bottom_edge_as_idle_lie():
    assert choose_edge_action("bottom", bottom_gap=0) == "idle_lie"


def test_choose_edge_action_uses_idle_lie_for_side_edge_near_bottom():
    assert choose_edge_action("right", bottom_gap=24, near_bottom_threshold=64) == "idle_lie"
