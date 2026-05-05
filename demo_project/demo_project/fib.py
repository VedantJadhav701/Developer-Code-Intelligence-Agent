def fibonacci(n):
    fib_list = [0, 1]
    for i in range(2, n):
        next_fib = fib_list[-1] + fib_list[-2]
        fib_list.append(next_fib)
    return fib_list[:n]

# Test cases
print(fibonacci(5))  # Expected: [0, 1, 1, 2, 3]
print(fibonacci(7))  # Expected: [0, 1, 1, 2, 3, 5, 8]