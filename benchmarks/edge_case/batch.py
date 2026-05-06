def process_batch(items):
    """Process a batch of items and return statistics."""
    # BUG: Crashes on empty list (division by zero in avg, index error in max/min)
    total = sum(items)
    avg = total / len(items)
    return {
        "total": total,
        "average": avg,
        "max": max(items),
        "min": min(items),
        "count": len(items),
    }

def find_outliers(items, threshold=2.0):
    """Find items that deviate from the mean by more than threshold * stdev."""
    # BUG: No guard for empty or single-item lists
    mean = sum(items) / len(items)
    variance = sum((x - mean) ** 2 for x in items) / len(items)
    stdev = variance ** 0.5
    return [x for x in items if abs(x - mean) > threshold * stdev]
