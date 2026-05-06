import pytest
from user_service import register_user

def test_register_valid():
    result = register_user("Alice", "alice@example.com")
    assert result["name"] == "Alice"
    assert result["active"] is True

def test_register_empty_name():
    with pytest.raises(ValueError, match="Name cannot be empty"):
        register_user("", "alice@example.com")

def test_register_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        register_user("Alice", "not-an-email")
