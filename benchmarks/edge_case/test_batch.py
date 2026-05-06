import pytest
from batch import process_batch, find_outliers

def test_process_normal():
    result = process_batch([1, 2, 3, 4, 5])
    assert result["total"] == 15
    assert result["average"] == 3.0
    assert result["count"] == 5

def test_process_empty():
    result = process_batch([])
    assert result["total"] == 0
    assert result["count"] == 0
    assert result["average"] == 0

def test_process_single():
    result = process_batch([42])
    assert result["total"] == 42
    assert result["average"] == 42

def test_find_outliers_empty():
    assert find_outliers([]) == []

def test_find_outliers_normal():
    result = find_outliers([1, 2, 3, 100])
    assert 100 in result
