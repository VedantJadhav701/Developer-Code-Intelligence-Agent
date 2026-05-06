# BUG: Wrong import name
from math_util import square, cube, factorial

def compute_stats(x):
    return {
        "square": square(x),
        "cube": cube(x),
        "factorial": factorial(x),
    }
