from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


DESTRUCTIVE_KEYWORDS = {
    "format",
    "rm -rf",
    "delete system",
    "registry",
    "powershell remove-item",
    "shutdown /s",
    "del /s",
}

HIGH_RISK_KEYWORDS = {
    "cmd.exe",
    "powershell",
    "bash",
    ".exe",
    ".bat",
    ".ps1",
    "reg add",
    "reg delete",
    "schtasks",
    "netsh",
    "curl",
    "wget",
}

MEDIUM_RISK_KEYWORDS = {
    "install",
    "download",
    "open browser",
    "upload",
    "move",
    "copy",
}


@dataclass
class GuardrailDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str
    risk: RiskLevel


def assess_action(text: str, allowlist_paths: Iterable[str]) -> GuardrailDecision:
    lowered = text.lower()
    for keyword in DESTRUCTIVE_KEYWORDS:
        if keyword in lowered:
            return GuardrailDecision(
                allowed=False,
                requires_confirmation=True,
                reason=f"Blocked destructive keyword: {keyword}",
                risk=RiskLevel.HIGH,
            )

    risk = RiskLevel.LOW
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in lowered:
            risk = RiskLevel.HIGH
            break
    if risk == RiskLevel.LOW:
        for keyword in MEDIUM_RISK_KEYWORDS:
            if keyword in lowered:
                risk = RiskLevel.MEDIUM
                break

    if not _path_allowed(lowered, allowlist_paths):
        return GuardrailDecision(
            allowed=False,
            requires_confirmation=True,
            reason="File action outside allowlist",
            risk=RiskLevel.MEDIUM,
        )

    requires_confirmation = risk in {RiskLevel.MEDIUM, RiskLevel.HIGH}
    return GuardrailDecision(
        allowed=True,
        requires_confirmation=requires_confirmation,
        reason=f"Risk level {risk.value}",
        risk=risk,
    )


def _path_allowed(text: str, allowlist_paths: Iterable[str]) -> bool:
    allowlist = [Path(path).as_posix().lower() for path in allowlist_paths]
    looks_like_path = (
        ":\\" in text
        or text.startswith("/")
        or "/" in text
        or "\\" in text
    )
    if not looks_like_path:
        return True
    return any(path and path in text for path in allowlist)
