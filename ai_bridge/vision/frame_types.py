from __future__ import annotations

from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class RedactedFrame:
    image: Image.Image
    redacted: bool = True

    def save(self, path: str) -> None:
        self.image.save(path)
