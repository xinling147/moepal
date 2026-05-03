import ctypes
import sys


class _LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def get_idle_seconds() -> int:
    if sys.platform != "win32":
        return 0

    try:
        last_input = _LastInputInfo()
        last_input.cbSize = ctypes.sizeof(_LastInputInfo)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input)):
            return 0

        tick_count = ctypes.windll.kernel32.GetTickCount()
        elapsed_ms = tick_count - last_input.dwTime
        if elapsed_ms < 0:
            return 0
        return int(elapsed_ms // 1000)
    except (AttributeError, OSError, TypeError, ValueError):
        return 0
