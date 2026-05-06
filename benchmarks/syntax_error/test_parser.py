from parser import parse_csv, parse_int_safe

def test_parse_csv():
    result = parse_csv("a, b, c\n1, 2, 3")
    assert len(result) == 2
    assert result[0] == ["a", "b", "c"]
    assert result[1] == ["1", "2", "3"]

def test_parse_int_safe():
    assert parse_int_safe("42") == 42
    assert parse_int_safe("abc") is None
    assert parse_int_safe(None) is None
