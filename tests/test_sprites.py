"""Tests for companion_app.animation.sprites — frame file discovery.

Tests the filesystem-logic layer (_discover_frame_files).  Pure stdlib, zero Qt.
QPixmap loading inside load_frames belongs to the integration layer.
"""

from pathlib import Path

import pytest

from companion_app.animation.sprites import _discover_frame_files


@pytest.fixture
def sprites_base(tmp_path):
    base = tmp_path / "sprites"
    base.mkdir()
    return base


# ---- TC-13: 正常动作返回非空帧文件列表 --------------------------------------

def test_discover_frames_returns_sorted_frame_files(sprites_base):
    action_dir = sprites_base / "tail_wag"
    action_dir.mkdir()
    _create_dummy_frame(action_dir, 0)
    _create_dummy_frame(action_dir, 1)
    _create_dummy_frame(action_dir, 2)

    result = _discover_frame_files("tail_wag", sprites_base)
    assert len(result) == 3
    assert all(isinstance(p, Path) for p in result)
    # Must be sorted
    assert result[0].name == "frame_000.png"
    assert result[1].name == "frame_001.png"
    assert result[2].name == "frame_002.png"


# ---- TC-14: 动作目录缺失时 fallback 到 idle_lie -----------------------------

def test_discover_frames_falls_back_to_idle_lie_when_action_missing(sprites_base):
    idle_dir = sprites_base / "idle_lie"
    idle_dir.mkdir()
    _create_dummy_frame(idle_dir, 0)
    _create_dummy_frame(idle_dir, 1)

    result = _discover_frame_files("nudge", sprites_base)
    assert len(result) == 2
    assert result[0].parent.name == "idle_lie"


# ---- TC-15: idle_lie 也缺失时返回空列表 ------------------------------------

def test_discover_frames_returns_empty_when_idle_lie_also_missing(sprites_base):
    result = _discover_frame_files("idle_lie", sprites_base)
    assert result == []


# ---- TC-16: 部分帧文件缺失 —— 只返回存在的文件 -----------------------------

def test_discover_frames_skips_missing_files(sprites_base):
    action_dir = sprites_base / "stretch"
    action_dir.mkdir()
    _create_dummy_frame(action_dir, 0)
    _create_dummy_frame(action_dir, 2)  # skip frame_001

    result = _discover_frame_files("stretch", sprites_base)
    assert len(result) == 2
    names = [p.name for p in result]
    assert "frame_000.png" in names
    assert "frame_002.png" in names
    assert "frame_001.png" not in names


# ---- TC-29: 空目录视为无帧，走 fallback ------------------------------------

def test_discover_frames_handles_empty_action_directory(sprites_base):
    action_dir = sprites_base / "nudge"
    action_dir.mkdir()  # exists but contains no PNGs

    idle_dir = sprites_base / "idle_lie"
    idle_dir.mkdir()
    _create_dummy_frame(idle_dir, 0)

    result = _discover_frame_files("nudge", sprites_base)
    # Falls back to idle_lie
    assert len(result) == 1
    assert result[0].parent.name == "idle_lie"


# ---- helper -----------------------------------------------------------------

def _create_dummy_frame(directory: Path, index: int, size: int = 64) -> None:
    import struct
    import zlib

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    raw = b""
    for y in range(size):
        raw += b"\x00"
        for x in range(size):
            raw += b"\xff\x00\x00\xff"

    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw))
    png += _chunk(b"IEND", b"")

    (directory / f"frame_{index:03d}.png").write_bytes(png)
