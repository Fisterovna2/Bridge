def test_import_safety() -> None:
    __import__("ai_bridge.core.orchestrator")
    __import__("ai_bridge.core.policy")
    __import__("ai_bridge.core.router")
