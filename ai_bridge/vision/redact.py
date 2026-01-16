from __future__ import annotations

from typing import Iterable

from PIL import Image, ImageDraw

from ai_bridge.vision.ocr import TextBox


def redact_image(image: Image.Image, pii_boxes: Iterable[TextBox]) -> Image.Image:
    redacted = image.copy()
    drawer = ImageDraw.Draw(redacted)
    for box in pii_boxes:
        left = max(0, box.left)
        top = max(0, box.top)
        right = max(left, box.left + box.width)
        bottom = max(top, box.top + box.height)
        drawer.rectangle([left, top, right, bottom], fill=(0, 0, 0))
    return redacted
