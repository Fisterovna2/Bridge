from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PIL import Image, ImageDraw

from ai_bridge.vision.ocr import TextBox


@dataclass(frozen=True)
class RedactedFrame:
    image: Image.Image
    redacted: bool = True

    def save(self, path: str) -> None:
        self.image.save(path)


def redact_image(image: Image.Image, pii_boxes: Iterable[TextBox]) -> RedactedFrame:
    redacted = image.copy()
    drawer = ImageDraw.Draw(redacted)
    for box in pii_boxes:
        left = max(0, box.left)
        top = max(0, box.top)
        right = max(left, box.left + box.width)
        bottom = max(top, box.top + box.height)
        drawer.rectangle([left, top, right, bottom], fill=(0, 0, 0))
    return RedactedFrame(image=redacted, redacted=True)
