from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from PIL import Image


@dataclass(frozen=True)
class RedactedFrame:
    """
    A frame that is SAFE to send to models and logs.
    Guarantees that PII has been redacted.
    """
    image: Image.Image
    redacted: bool = True
    meta: Dict[str, Any] | None = None

    def __post_init__(self):
        if self.meta is None:
            object.__setattr__(self, "meta", {})
