from __future__ import annotations

import ctypes
import sys
from typing import Any


HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


def build_topmost_flags() -> int:
    return SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW


def ensure_window_topmost(widget: Any, *, user32: Any | None = None) -> bool:
    try:
        hwnd = int(widget.winId())
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return False

    if hwnd == 0:
        return False

    if user32 is None:
        if sys.platform != "win32":
            return False
        user32 = ctypes.windll.user32

    result = user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        build_topmost_flags(),
    )
    return bool(result)


__all__ = ["build_topmost_flags", "ensure_window_topmost"]
