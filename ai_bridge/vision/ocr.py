from __future__ import annotations

from dataclasses import dataclass
from typing import List

from PIL import Image


@dataclass
class TextBox:
    text: str
    left: int
    top: int
    width: int
    height: int


class OcrEngine:
    def detect_text_boxes(self, image: Image.Image) -> List[TextBox]:
        import pytesseract

        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        boxes: List[TextBox] = []
        for i, text in enumerate(data.get("text", [])):
            if not text.strip():
                continue
            boxes.append(
                TextBox(
                    text=text,
                    left=int(data["left"][i]),
                    top=int(data["top"][i]),
                    width=int(data["width"][i]),
                    height=int(data["height"][i]),
                )
            )
        return boxes
