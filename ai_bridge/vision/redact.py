from __future__ import annotations

from typing import Iterable, List, Protocol, TYPE_CHECKING

from PIL import Image, ImageDraw

from ai_bridge.vision.frame_types import RedactedFrame

if TYPE_CHECKING:
    # В рантайме НЕ импортим ocr.py, чтобы не было циклических импортов
    from ai_bridge.vision.ocr import TextBox


class BoxLike(Protocol):
    left: int
    top: int
    width: int
    height: int


def redact_image(image: Image.Image, pii_boxes: Iterable[BoxLike]) -> RedactedFrame:
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


# Чтобы старые импорты тоже работали:
__all__ = ["RedactedFrame", "redact_image"]
