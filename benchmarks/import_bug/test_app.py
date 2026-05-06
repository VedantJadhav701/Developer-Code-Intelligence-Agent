from app import compute_stats

def test_compute_stats():
    result = compute_stats(3)
    assert result["square"] == 9
    assert result["cube"] == 27
    assert result["factorial"] == 6

def test_compute_stats_one():
    result = compute_stats(1)
    assert result["square"] == 1
    assert result["factorial"] == 1
