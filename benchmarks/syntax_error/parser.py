def parse_csv(text):
    """Parse a CSV string into a list of lists."""
    rows = []
    for line in text.strip().split("\n"):
        # BUG: missing closing bracket
        cols = [c.strip() for c in line.split(",")
        rows.append(cols)
    return rows

def parse_int_safe(value):
    """Parse a string to int, return None on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
