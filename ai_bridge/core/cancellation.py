from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass
class CancellationToken:
    _event: threading.Event

    @classmethod
    def create(cls) -> "CancellationToken":
        return cls(threading.Event())

    def cancel(self) -> None:
        self._event.set()

    def reset(self) -> None:
        self._event.clear()

    def is_cancelled(self) -> bool:
        return self._event.is_set()
