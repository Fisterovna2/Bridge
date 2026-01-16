from enum import Enum


class RunMode(str, Enum):
    NORMAL = "normal"
    GAME = "game"
    SANDBOX = "sandbox"
