from ai_bridge.game.calibration import compute_calibration


def test_calibration_mapping() -> None:
    calibration = compute_calibration(100, 100, 200, 300)
    mapped = calibration.map_point(50, 50)
    assert mapped == (100, 150)
