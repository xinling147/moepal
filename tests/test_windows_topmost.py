from companion_app.platform.windows_topmost import build_topmost_flags, ensure_window_topmost


class _FakeWindow:
    def __init__(self, hwnd: int):
        self._hwnd = hwnd

    def winId(self):
        return self._hwnd


class _FakeUser32:
    def __init__(self):
        self.calls = []

    def SetWindowPos(self, *args):
        self.calls.append(args)
        return 1


def test_ensure_window_topmost_calls_set_window_pos_without_moving_or_resizing():
    user32 = _FakeUser32()

    assert ensure_window_topmost(_FakeWindow(1234), user32=user32) is True

    assert user32.calls == [
        (1234, -1, 0, 0, 0, 0, build_topmost_flags())
    ]


def test_ensure_window_topmost_ignores_missing_window_handle():
    user32 = _FakeUser32()

    assert ensure_window_topmost(_FakeWindow(0), user32=user32) is False

    assert user32.calls == []
