from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

from ai_bridge.vision.ocr import TextBox


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


@dataclass
class PiiMatch:
    text: str
    pattern: str


class PiiDetector:
    def __init__(self, custom_patterns: Iterable[re.Pattern[str]] | None = None) -> None:
        self.patterns = [EMAIL_RE, PHONE_RE, CARD_RE]
        if custom_patterns:
            self.patterns.extend(custom_patterns)

    def detect(self, text: str) -> List[PiiMatch]:
        matches: List[PiiMatch] = []
        for pattern in self.patterns:
            for match in pattern.finditer(text):
                matches.append(PiiMatch(text=match.group(0), pattern=pattern.pattern))
        return matches

    def find_pii_boxes(self, boxes: Iterable[TextBox]) -> List[TextBox]:
        pii_boxes: List[TextBox] = []
        for box in boxes:
            if self.detect(box.text):
                pii_boxes.append(box)
        return pii_boxes
