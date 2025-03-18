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

### plagiarism_detector/
A comprehensive tool for checking similarities between text documents and detecting potential plagiarism:
- Multiple similarity metrics (Cosine, Jaccard, Sequence, N-gram)
- Interactive HTML reports with color-coded similarity highlighting
- Paragraph-by-paragraph comparison
- Sentence-level analysis
- Shared phrase detection
- Similarity heatmap visualization
- Support for multiple file formats (TXT, PDF, DOCX, LaTeX)

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

## Logging Configuration

The logging system is configured via `logging_config.json` which defines:
- Multiple formatters (simple text and JSON)
- Different handlers (console, file)
- Queue-based async logging

Log files are stored in the `logs/` directory in JSON Lines format.

## Using the Plagiarism Detector

The plagiarism detector can be used to compare two documents and assess their similarity.

### Command Line Interface

```bash
python plagiarism_cli.py file1.txt file2.txt [options]
```

#### Options:
- `--title1 "Title 1"`: Set a custom title for the first document
- `--title2 "Title 2"`: Set a custom title for the second document
- `--threshold 0.7`: Set similarity threshold (0.0 to 1.0)
- `--output-dir "results"`: Specify output directory
- `--formats html json text summary chart heatmap gauge`: Choose output format(s)
- `--verbose`: Enable detailed output

### Example Usage

Basic comparison of two text files:
```bash
python plagiarism_cli.py document1.txt document2.txt
```

Comparing a thesis with a published paper:
```bash
python plagiarism_cli.py thesis.pdf paper.pdf --title1 "My Thesis" --title2 "Journal Paper" --formats all
```

Comparing with lower similarity threshold:
```bash
python plagiarism_cli.py file1.docx file2.docx --threshold 0.5
```

### Python API

You can also use the detector in your own Python scripts:

```python
from plagiarism_detector import PlagiarismDetector

# Initialize detector
detector = PlagiarismDetector(threshold=0.7)

# Analyze documents
result = detector.analyze("document1.txt", "document2.txt")

# Access similarity metrics
similarity = result["comparison"]["similarity_metrics"]["combined_similarity"]
print(f"Overall similarity: {similarity:.2f}")

# Get paths to generated reports
html_report = result["reports"]["html"]
print(f"HTML report generated: {html_report}")
```

## File Structure

```
python_learning/
│
├── coding_habits.py         # Python best practices examples
├── logger.py                # Custom JSON logging implementation
├── logging_config.json      # Logging configuration
├── main.py                  # Example application
├── plagiarism_cli.py        # Command-line interface for plagiarism detector
│
├── plagiarism_detector/     # Plagiarism detection package
│   ├── __init__.py          # Package initialization
│   ├── detector.py          # Core plagiarism detection functionality
│   ├── text_processor.py    # Text processing utilities
│   ├── visualizer.py        # Visualization tools
│   ├── report_generator.py  # Report generation utilities
│   └── file_handler.py      # File loading/saving utilities
│
├── logs/                    # Log file directory
│   └── logger.log.jsonl     # JSON Line formatted logs
│
├── personal_files/          # Directory for personal files (contents ignored by Git)
│   ├── .gitkeep             # Empty file to maintain directory structure
│   ├── document1.txt        # Sample document for plagiarism detection (not in Git)
│   ├── document2.txt        # Sample document for plagiarism detection (not in Git)
│   └── plagiarism_results/  # Results from plagiarism detection (not in Git)
│
├── requirements.txt         # Project dependencies
├── .gitignore               # Git ignore patterns
└── README.md                # Project documentation
```

## Personal Files

The repository includes a `personal_files/` directory whose structure is tracked by Git, but contents are ignored (via .gitignore). 
You can use this directory to store:
- Personal notes
- Configuration files with credentials
- Local development settings
- Test documents for plagiarism detection
- Any other files that shouldn't be committed to version control

The directory structure itself is maintained in Git using a `.gitkeep` placeholder file.

## Contributing

Feel free to add more examples of Python best practices or improvements to the existing code.