"""
Demo project: A simple calculator with an intentional bug for the agent to fix.
"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    # BUG: No zero-division guard
    return a / b