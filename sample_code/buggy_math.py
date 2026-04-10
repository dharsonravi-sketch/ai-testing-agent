# sample_code/buggy_math.py

def divide(a, b):
    return a / b              # Bug: crashes on divide by zero

def is_palindrome(s):
    return s == s[::-1]       # Bug: case sensitive, ignores spaces

def find_max(lst):
    max_val = 0               # Bug: fails for all-negative lists
    for x in lst:
        if x > max_val:
            max_val = x
    return max_val
