from ai_bridge.vision.pii import PiiDetector


def test_pii_detector_finds_email_phone_card() -> None:
    detector = PiiDetector()
    text = "Contact test@example.com or +1 (555) 123-4567. Card 4111 1111 1111 1111"
    matches = detector.detect(text)
    patterns = {match.text for match in matches}
    assert "test@example.com" in patterns
    assert "+1 (555) 123-4567" in patterns
    assert "4111 1111 1111 1111" in patterns
