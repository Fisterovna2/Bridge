from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from PIL import Image, ImageDraw

from ai_bridge.vision.ocr import TextBox


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


def redact_image(image: Image.Image, pii_boxes: Iterable[TextBox]) -> RedactedFrame:
    """
    Redact PII regions in the image and return a RedactedFrame.
    """
    redacted_img = image.copy()
    drawer = ImageDraw.Draw(redacted_img)

    for box in pii_boxes:
        left = max(0, box.left)
        top = max(0, box.top)
        right = max(left, box.left + box.width)
        bottom = max(top, box.top + box.height)
        drawer.rectangle([left, top, right, bottom], fill=(0, 0, 0))

    return RedactedFrame(
        image=redacted_img,
        meta={
            "pii_boxes": len(list(pii_boxes)),
            "size": redacted_img.size,
        },
    )
