from __future__ import annotations

import hashlib
from pathlib import Path

from companion_app.paths import get_sprites_dir


MIN_FRAME_COUNTS = {
    "idle_lie": 6,
    "sleep": 4,
    "peek": 6,
    "nudge": 6,
    "tail_wag": 6,
    "happy_bounce": 6,
    "look_around": 4,
    "sit_wait": 4,
}


def test_primary_cat_actions_have_enough_frames():
    sprites_dir = get_sprites_dir()

    for action_id, expected_count in MIN_FRAME_COUNTS.items():
        frames = sorted((sprites_dir / action_id).glob("frame_*.png"))

        assert len(frames) >= expected_count, action_id


def test_primary_cat_action_frames_are_contiguously_numbered():
    sprites_dir = get_sprites_dir()

    for action_id in MIN_FRAME_COUNTS:
        frames = sorted((sprites_dir / action_id).glob("frame_*.png"))
        expected_names = [f"frame_{index:03d}.png" for index in range(len(frames))]

        assert [frame.name for frame in frames] == expected_names, action_id


def test_primary_cat_actions_have_visible_frame_variation():
    sprites_dir = get_sprites_dir()

    for action_id in MIN_FRAME_COUNTS:
        frames = sorted((sprites_dir / action_id).glob("frame_*.png"))
        hashes = {_sha256(frame) for frame in frames}

        assert len(hashes) >= 2, action_id


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
