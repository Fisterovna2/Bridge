from __future__ import annotations

import time

import pyautogui

from ai_bridge.core.actions import Action, ActionType


class HostInputController:
    def apply_action(self, action: Action) -> None:
        if action.action_type == ActionType.MOVE and action.x is not None and action.y is not None:
            pyautogui.moveTo(action.x, action.y, duration=action.duration_ms / 1000)
        elif action.action_type == ActionType.CLICK and action.x is not None and action.y is not None:
            pyautogui.click(action.x, action.y)
        elif action.action_type == ActionType.TYPE and action.text is not None:
            pyautogui.typewrite(action.text)
        elif action.action_type == ActionType.WAIT:
            time.sleep(action.duration_ms / 1000)
