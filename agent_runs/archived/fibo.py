import sys

def fibonacci(n):
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def main():
    if len(sys.argv) != 2:
        print("Usage: python fibo.py <n>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
        result = fibonacci(n)
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
