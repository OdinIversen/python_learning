# Python Learning Repository

A collection of Python modules and utilities demonstrating best practices in Python development.

## Modules

### coding_habits.py
Contains practical examples of Python best practices, including:
- Data types and their properties (immutable vs mutable, usage examples)
- String formatting with f-strings
- Path manipulation with pathlib
- File operations
- Exception handling
- Using default parameters safely
- Comprehensions (list, dict, set, generator)
- Type checking with isinstance
- Comparing singletons (None, True, False)
- Advanced iteration techniques (enumerate, zip, reversed)
- Performance timing with time.perf_counter()
- Logical operators (and, or) behavior
- Named tuples and dataclasses

### logger.py
A custom JSON logging implementation with:
- Custom JSON formatter (MyJSONFormatter)
- Log filtering (NonErrorFilter)
- Structured logging support with proper formatting
- Built-in attribute handling

### logging_config.json
Configuration for the logging system:
- Multiple formatters (simple text and JSON)
- Different handlers (stderr, rotating file)
- Queue-based async logging
- Log level settings

### main.py
Example application demonstrating the logging system:
- Configuration loading from JSON
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Exception logging with traceback
- Queue-based logging with listener
- Proper cleanup using atexit

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/python_learning.git
cd python_learning
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the main application
```bash
python main.py
```

## Logging System

The logging system is configured via `logging_config.json` which defines:
- Formatters: simple text and a custom JSON formatter
- Handlers: stderr (for warnings and above) and rotating file handler
- Queue-based async logging for thread safety

Log files are stored in the `logs/` directory in JSON Lines format (.jsonl).

Each log entry contains:
- Level (DEBUG, INFO, etc.)
- Message content
- Timestamp (ISO format with timezone)
- Logger name
- Module, function, and line number
- Thread information

## Project Structure

```
python_learning/
│
├── coding_habits.py         # Python best practices examples
├── logger.py                # Custom JSON logging implementation
├── logging_config.json      # Logging configuration
├── main.py                  # Example application with logging demo
│
├── logs/                    # Log file directory
│   └── logger.log.jsonl     # JSON Line formatted logs
│
├── personal_files/          # Directory for personal files (contents ignored by Git)
│   └── .gitkeep             # Empty file to maintain directory structure
│
├── requirements.txt         # Project dependencies (not yet created)
├── .gitignore               # Git ignore patterns
└── README.md                # Project documentation
```

## Personal Files

The repository includes a `personal_files/` directory whose structure is tracked by Git, but contents are ignored (via .gitignore). 
You can use this directory to store:
- Personal notes
- Configuration files with credentials
- Local development settings
- Test data and examples
- Any other files that shouldn't be committed to version control

The directory structure itself is maintained in Git using a `.gitkeep` placeholder file.

## Future Improvements

Potential areas for expansion:
- Add more advanced Python patterns and techniques
- Create unit tests for modules
- Add a CLI interface
- Implement async/await examples
- Add type checking with mypy
- Create example of packaging Python code

## Contributing

Feel free to add more examples of Python best practices or improvements to the existing code.