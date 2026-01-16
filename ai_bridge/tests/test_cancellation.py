from ai_bridge.core.cancellation import CancellationToken


def test_cancellation_token() -> None:
    token = CancellationToken.create()
    assert token.is_cancelled() is False
    token.cancel()
    assert token.is_cancelled() is True
    token.reset()
    assert token.is_cancelled() is False
