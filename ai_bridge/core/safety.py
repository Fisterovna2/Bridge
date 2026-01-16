from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


DESTRUCTIVE_KEYWORDS = {
    "format",
    "rm -rf",
    "delete system",
    "registry",
    "powershell remove-item",
    "shutdown /s",
    "del /s",
}


@dataclass
class GuardrailDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str


def assess_action(text: str, allowlist_paths: Iterable[str]) -> GuardrailDecision:
    lowered = text.lower()
    for keyword in DESTRUCTIVE_KEYWORDS:
        if keyword in lowered:
            return GuardrailDecision(
                allowed=False,
                requires_confirmation=True,
                reason=f"Blocked destructive keyword: {keyword}",
            )
    for path in allowlist_paths:
        if path.lower() in lowered:
            return GuardrailDecision(
                allowed=True,
                requires_confirmation=False,
                reason="Path allowlisted",
            )
    return GuardrailDecision(
        allowed=True,
        requires_confirmation=True,
        reason="Action outside allowlist requires confirmation",
    )
