from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Protocol, TYPE_CHECKING

from PIL import Image, ImageDraw

if TYPE_CHECKING:
    # Только для подсказок типов. В рантайме НЕ импортим ocr.py (разрываем циклы).
    from ai_bridge.vision.ocr import TextBox


class BoxLike(Protocol):
    left: int
    top: int
    width: int
    height: int


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


def redact_image(image: Image.Image, pii_boxes: Iterable[BoxLike]) -> RedactedFrame:
    """
    Redact PII regions in the image and return a RedactedFrame.
    """
    boxes: List[BoxLike] = list(pii_boxes)

    redacted_img = image.copy()
    drawer = ImageDraw.Draw(redacted_img)

    for box in boxes:
        left = max(0, int(box.left))
        top = max(0, int(box.top))
        right = max(left, int(box.left + box.width))
        bottom = max(top, int(box.top + box.height))
        drawer.rectangle([left, top, right, bottom], fill=(0, 0, 0))

    return RedactedFrame(
        image=redacted_img,
        meta={"pii_boxes": len(boxes), "size": redacted_img.size},
    )
