def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    # CORRECTED: Guard against division by zero
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

# Test function to ensure the calculator works as expected
def test_divide_by_zero():
    with pytest.raises(ValueError) as e_info:
        divide(10, 0)
    assert str(e_info.value) == "Division by zero is not allowed."