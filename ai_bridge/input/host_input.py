from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple

_PYAUTOGUI_OK = False
_PYAUTOGUI_ERR: Optional[BaseException] = None
_pyautogui: Any = None


def _load_pyautogui() -> bool:
    """
    Lazy-load pyautogui so importing this module doesn't crash in headless CI.
    On Linux CI runners DISPLAY is often unset; importing pyautogui/mouseinfo will crash.
    """
    global _PYAUTOGUI_OK, _PYAUTOGUI_ERR, _pyautogui

    if _pyautogui is not None:
        return _PYAUTOGUI_OK

    try:
        # Headless guard: pyautogui on Linux requires DISPLAY
        if os.name != "nt" and not os.environ.get("DISPLAY"):
            raise RuntimeError("Host input unavailable: DISPLAY is not set (headless environment).")

        import pyautogui  # type: ignore

        _pyautogui = pyautogui
        _PYAUTOGUI_OK = True
        _PYAUTOGUI_ERR = None
        return True
    except BaseException as e:
        _pyautogui = None
        _PYAUTOGUI_OK = False
        _PYAUTOGUI_ERR = e
        return False


@dataclass(frozen=True)
class InputEvent:
    """
    Generic input event container used by orchestrator.
    kind: 'mouse_move' | 'mouse_click' | 'key_text' | 'key_press' | 'key_down' | 'key_up'
    """
    kind: str
    x: int | None = None
    y: int | None = None
    button: str | None = None
    text: str | None = None
    key: str | None = None


class HostInputController:
    """
    Controls host mouse/keyboard input using pyautogui.
    In headless environments this becomes unavailable but MUST NOT crash imports/tests.
    """

    def __init__(self) -> None:
        self._available = _load_pyautogui()

    @property
    def available(self) -> bool:
        return self._available

    def explain_unavailable(self) -> str:
        if self._available:
            return "Host input is available."
        return f"Host input is unavailable in this environment: {_PYAUTOGUI_ERR!r}"

    def send(self, events: Iterable[InputEvent]) -> None:
        if not self._available:
            raise RuntimeError(self.explain_unavailable())

        pa = _pyautogui
        assert pa is not None

        for ev in events:
            if ev.kind == "mouse_move":
                if ev.x is None or ev.y is None:
                    continue
                pa.moveTo(int(ev.x), int(ev.y))
            elif ev.kind == "mouse_click":
                if ev.x is not None and ev.y is not None:
                    pa.click(int(ev.x), int(ev.y), button=ev.button or "left")
                else:
                    pa.click(button=ev.button or "left")
            elif ev.kind == "key_text":
                if ev.text:
                    pa.write(str(ev.text))
            elif ev.kind == "key_press":
                if ev.key:
                    pa.press(str(ev.key))
            elif ev.kind == "key_down":
                if ev.key:
                    pa.keyDown(str(ev.key))
            elif ev.kind == "key_up":
                if ev.key:
                    pa.keyUp(str(ev.key))
            else:
                # Unknown event type, ignore
                continue
