# Python Learning Repository

A collection of Python modules and utilities demonstrating best practices in Python development.

## Modules

### coding_habits.py
Contains practical examples of Python best practices, including:
- Data types and their properties
- String formatting with f-strings
- Path manipulation with pathlib
- File operations
- Exception handling
- Comprehensions (list, dict, set)
- Type checking
- Iteration techniques
- Performance timing
- Named tuples and dataclasses

### logger.py
A custom JSON logging implementation with:
- Custom JSON formatter
- Log filtering
- Structured logging support

### main.py
Example application demonstrating the logging system:
- Configuration loading from JSON
- Multiple log levels
- Exception logging
- Queue-based logging with listener

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

3. Run the main application
```bash
python main.py
```

## Logging Configuration

The logging system is configured via `logging_config.json` which defines:
- Multiple formatters (simple text and JSON)
- Different handlers (console, file)
- Queue-based async logging

Log files are stored in the `logs/` directory in JSON Lines format.

## File Structure

```
python_learning/
│
├── coding_habits.py      # Python best practices examples
├── logger.py             # Custom JSON logging implementation
├── logging_config.json   # Logging configuration
├── main.py               # Example application
│
├── logs/                 # Log file directory
│   └── logger.log.jsonl  # JSON Line formatted logs
│
├── personal_files/       # Directory for personal files (contents ignored by Git)
│   └── .gitkeep          # Empty file to maintain directory structure
│
├── .gitignore            # Git ignore patterns
└── README.md             # Project documentation
```

## Personal Files

The repository includes a `personal_files/` directory whose structure is tracked by Git, but contents are ignored (via .gitignore). 
You can use this directory to store:
- Personal notes
- Configuration files with credentials
- Local development settings
- Any other files that shouldn't be committed to version control

The directory structure itself is maintained in Git using a `.gitkeep` placeholder file.

## Contributing

Feel free to add more examples of Python best practices or improvements to the existing code.