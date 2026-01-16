from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    MOVE = "move"
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"


@dataclass
class Action:
    action_type: ActionType
    x: int | None = None
    y: int | None = None
    text: str | None = None
    duration_ms: int = 0
