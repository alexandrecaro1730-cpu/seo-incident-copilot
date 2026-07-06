from seo_incident_copilot.detectors.rank_drop import detect_rank_drop


def test_rank_drop_triggers_for_major_drop():
    snapshot = {"old_position": 2, "new_position": 9, "business_priority": "high"}
    result = detect_rank_drop(snapshot, threshold=5)
    assert result["triggered"] is True
    assert result["positions_lost"] == 7
    assert result["severity"] == "high"


def test_rank_drop_does_not_trigger_for_noise():
    snapshot = {"old_position": 5, "new_position": 6, "business_priority": "low"}
    result = detect_rank_drop(snapshot, threshold=5)
    assert result["triggered"] is False
