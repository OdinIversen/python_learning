from collections import namedtuple

def data_types():
    # Integer (int)
    # Immutable: cannot be changed after creation
    # Supports arithmetic operations: +, -, *, /, etc.
    # Example:
    example_int = 42

    # Float
    # Immutable: represents floating-point numbers (decimal)
    # Supports arithmetic operations with precision
    # Example:
    example_float = 3.14159

    # Boolean (bool)
    # Immutable: represents True or False
    # Used in logical operations and control flow
    # Example:
    example_bool = True

    # String (str)
    # Immutable: sequence of characters, cannot be changed after creation
    # Supports indexing, slicing, and many methods (e.g., .upper(), .find())
    # Example:
    example_str = "Hello, World!"

    # List
    # Mutable: ordered collection, elements can be modified
    # Allows duplicates and supports indexing, slicing
    # Example:
    example_list = ["apple", "banana", "cherry"]

    # Tuple
    # Immutable: ordered collection, elements cannot be modified
    # Allows duplicates, supports indexing, slicing
    # Example:
    example_tuple = (10.0, 20.0)

    # Set
    # Mutable: unordered collection of unique elements, no duplicates
    # Supports fast membership testing, set operations (union, intersection)
    # Example:
    example_set = {1, 2, 3, 3, 4}

    # Dictionary (dict)
    # Mutable: key-value pairs, keys are unique and immutable
    # Fast lookups, supports addition, modification, deletion of key-value pairs
    # Example:
    example_dict = {"Alice": 90, "Bob": 85}

    # Generator
    # Lazy evaluation: yields items one at a time, memory efficient
    # Single-use, suitable for large or infinite sequences
    # Example:
    example_gen = (x * x for x in range(5))  # Generates squares: 0, 1, 4, 9, 16

    # Bytes
    # Immutable: sequence of bytes (8-bit values), used for binary data
    # Supports indexing, slicing
    # Example:
    example_bytes = b"hello"

    # Bytearray
    # Mutable: like bytes, but can be modified
    # Used for handling binary data that needs to be changed
    # Example:
    example_bytearray = bytearray(b"hello")
    example_bytearray[0] = 72  # Changes 'h' to 'H'

    # NoneType
    # Singleton object: represents the absence of value or a null value
    # Often used as a default argument in functions
    # Example:
    example_none = None

def string_formatting():
    text = "formatting strings."
    print(f"Always use f-string for {text}")
    x = 1.23456789
    print(f"Rounded to 2 decimal places: {x:.2f}")

def manipulating_paths():
    import pathlib
    path = pathlib.Path("folder/file.txt")
    print(path.name)  # file.txt
    print(path.stem)  # file
    print(path.suffix)  # .txt
    print(path.parent)  # folder
    print(path.exists())  # True

def using_files():
    with open("file.txt", "r") as file:
        for line in file:
            print(line)

def using_exceptions():
    try:
        print(1/0)
    except ValueError as e:
        print(f"ValueError: {e}")

def passing_default_mutables(list=None):
    if list is None:
        list = []
    print(list)

def using_comprehensions():
    dictionary_comp = {i: i**2 for i in range(10)}
    list_comp = [i for i in range(10) if i % 2 == 0]
    set_comp = {i for i in range(10) if i % 2 == 0}
    generator_comp = (i for i in range(10) if i % 2 == 0)

def checking_type_equality():
    Point = namedtuple("Point", ["x", "y"])
    p1 = Point(1, 2)

    if isinstance(p1, Point):
        print("p1 is a Point object")

def comparing_singletons(x):
    # Singletons are objects that are created only once in memory.
    if x is None:
        pass
    if x is True:
        pass
    if x is False:
        pass

def iterating_over_sequences():
    # Example 1: Basic Iteration
    elements = ["apple", "banana", "cherry"]
    for element in elements:
        print(element)

    # Example 2: Iterating with Index
    for i, element in enumerate(elements):
        print(f"Index {i}: {element}")

    # Example 3: Iterating Over Two Lists in Parallel using zip
    list1 = [1, 2, 3]
    list2 = ["one", "two", "three"]
    for num, word in zip(list1, list2):
        print(f"{num}: {word}")

    # Example 4: Iterating Over a Dictionary
    my_dict = {"name": "Alice", "age": 30, "city": "New York"}
    for key, value in my_dict.items():
        print(f"{key}: {value}")

    # Example 5: Iterating in Reverse
    for element in reversed(elements):
        print(element)

def timing_code():
    import time
    start_time = time.perf_counter()
    time.sleep(1)
    end_time = time.perf_counter()
    print(f"Execution Time: {end_time - start_time:0.4f} seconds")

def doing_math():
    import numpy as np
    import pandas as pd

    divmod(9, 2)  # (4, 1)
def and_or():
    # or returns the first truthy value or the last falsy value
    print(0 or 1)  # 1
    # and returns the first falsy value or the last truthy value
    print(0 and 1)  # 0

from typing import NamedTuple
class Point(NamedTuple):
    x: int
    y: int

from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int

# Learn to package code, and install it in a virtual environment
# Learn debugging techniques, and how to use a debugger

def main():
    return

if __name__ == "__main__":
    main()