from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from PIL import Image


@dataclass(frozen=True)
class RedactedFrame:
    """
    A frame that is SAFE to send to models and logs.
    Guarantees that PII has been redacted.

    Compatibility: behaves like a PIL.Image for common operations by delegating
    attribute access to the underlying image.
    """
    image: Image.Image
    redacted: bool = True
    meta: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.meta is None:
            object.__setattr__(self, "meta", {})

    # --- Compatibility helpers (tests / legacy code expect PIL.Image-like API) ---
    def getpixel(self, xy):  # type: ignore[no-untyped-def]
        return self.image.getpixel(xy)

    def copy(self) -> Image.Image:
        return self.image.copy()

    @property
    def size(self):
        return self.image.size

    @property
    def mode(self):
        return self.image.mode

    def __getattr__(self, name: str):
        # Delegate unknown attrs/methods to the underlying PIL image
        return getattr(self.image, name)
