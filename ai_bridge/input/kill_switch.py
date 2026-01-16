from __future__ import annotations

from typing import Callable

from pynput import keyboard, mouse

from ai_bridge.core.cancellation import CancellationToken


class KillSwitchListener:
    def __init__(self, token: CancellationToken, on_cancel: Callable[[str], None]) -> None:
        self.token = token
        self.on_cancel = on_cancel
        self._mouse_listener = mouse.Listener(
            on_move=self._cancel,
            on_click=self._cancel,
            on_scroll=self._cancel,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._cancel,
            on_release=self._cancel,
        )

    def start(self) -> None:
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        self._mouse_listener.stop()
        self._keyboard_listener.stop()

    def _cancel(self, *args, **kwargs) -> None:
        if not self.token.is_cancelled():
            self.token.cancel()
            self.on_cancel("Cancelled by user input")
