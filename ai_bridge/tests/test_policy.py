from ai_bridge.core.modes import RunMode
from ai_bridge.core.policy import PolicyEngine
from ai_bridge.core.safety import RiskLevel


def test_policy_normal_requires_confirmation_for_high_risk() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate(RunMode.NORMAL, "run powershell script", ["Documents"])
    assert decision.requires_confirmation is True
    assert decision.risk == RiskLevel.HIGH
    assert decision.rule_id == "confirm-high-risk"


def test_policy_game_allows_with_confirmation() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate(RunMode.GAME, "run powershell script", ["Documents"])
    assert decision.allowed is True
    assert decision.requires_confirmation is True
    assert decision.rule_id == "confirm-high-risk-vm"


def test_policy_sandbox_allows() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate(RunMode.SANDBOX, "open notepad", ["Documents"])
    assert decision.allowed is True
    assert decision.requires_confirmation is False
    assert decision.rule_id == "allow"
