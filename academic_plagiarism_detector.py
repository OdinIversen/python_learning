import difflib
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
import re
from dataclasses import dataclass

@dataclass
class TextComparison:
    """Data class to store text comparison results."""
    similarity_ratio: float
    similarity_by_paragraph: List[float]
    html_diff: str

def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs, maintaining LaTeX citations and commands.
    """
    # Remove trailing whitespace from lines
    text = re.sub(r' +$', '', text, flags=re.MULTILINE)
    
    # Split by double newlines or paragraph breaks
    paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
    
    # Filter out empty paragraphs
    return [p.strip() for p in paragraphs if p.strip()]

def normalize_academic_text(text: str) -> str:
    """
    Normalize academic text for better comparison while preserving important elements:
    - Convert to lowercase
    - Normalize whitespace
    - Preserve LaTeX commands and citations
    """
    # Temporarily protect LaTeX commands and citations
    protected_elements = []
    
    def protect_latex(match):
        protected_elements.append(match.group(0))
        return f"__PROTECTED_{len(protected_elements)-1}__"
    
    # Protect LaTeX citations and commands
    latex_pattern = r'\\[a-zA-Z]+\{[^}]*\}|\\[a-zA-Z]+'
    protected_text = re.sub(latex_pattern, protect_latex, text)
    
    # Normalize
    normalized = protected_text.lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Restore protected elements
    for i, element in enumerate(protected_elements):
        normalized = normalized.replace(f"__PROTECTED_{i}__", element)
    
    return normalized.strip()

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts."""
    sequence_matcher = difflib.SequenceMatcher(None, text1, text2)
    return sequence_matcher.ratio()

def generate_html_diff(text1: str, text2: str, filename1: str, filename2: str, 
                       para_similarities: Optional[List[float]] = None) -> str:
    """
    Generate HTML showing differences between two texts with highlights.
    Copied text will be highlighted in yellow.
    """
    # Split texts into paragraphs for better comparison
    paragraphs1 = split_into_paragraphs(text1)
    paragraphs2 = split_into_paragraphs(text2)
    
    # Create HTML with custom styling
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Academic Text Comparison</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .container {
            display: flex;
            margin-bottom: 30px;
        }
        .column {
            flex: 1;
            padding: 0 15px;
            border: 1px solid #ddd;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .document-title {
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
            color: #333;
        }
        .paragraph {
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #eee;
        }
        .similarity {
            padding: 10px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            font-size: 16px;
        }
        .similar-high {
            background-color: #FFFF77;
        }
        .similar-medium {
            background-color: #FFFFBB;
        }
        .similar-low {
            background-color: #FFFFEE;
        }
        .para-similarity {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        .highlight {
            background-color: #FFFF77;
            padding: 1px 0;
        }
        .diff-html {
            margin-top: 40px;
            border-top: 2px solid #ddd;
            padding-top: 20px;
        }
        .latex-command {
            color: #0066cc;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Academic Text Comparison</h1>
"""
    
    # Add overall similarity info
    overall_similarity = calculate_similarity(
        normalize_academic_text(text1), 
        normalize_academic_text(text2)
    )
    html += f'<div class="similarity">Overall similarity: {overall_similarity:.2%}</div>'

    # Add side-by-side comparison
    html += '<div class="container">'
    
    # Document 1 column
    html += f'<div class="column"><div class="document-title">Document 1: {filename1}</div>'
    for i, para in enumerate(paragraphs1):
        similarity_class = ""
        similarity_info = ""
        
        if para_similarities and i < len(para_similarities):
            sim = para_similarities[i]
            similarity_info = f'<div class="para-similarity">Similarity: {sim:.2%}</div>'
            
            if sim > 0.8:
                similarity_class = "similar-high"
            elif sim > 0.5:
                similarity_class = "similar-medium"
            elif sim > 0.3:
                similarity_class = "similar-low"
        
        html += f'<div class="paragraph {similarity_class}">{similarity_info}{para}</div>'
    
    html += '</div>'
    
    # Document 2 column
    html += f'<div class="column"><div class="document-title">Document 2: {filename2}</div>'
    for para in paragraphs2:
        html += f'<div class="paragraph">{para}</div>'
    html += '</div></div>'
    
    # Add detailed diff view
    html += '<div class="diff-html"><h2>Detailed Line-by-Line Comparison</h2>'
    diff_generator = difflib.HtmlDiff(tabsize=4)
    diff_html = diff_generator.make_file(
        text1.splitlines(),
        text2.splitlines(),
        filename1,
        filename2,
        context=True
    )
    
    # Extract just the table part of the diff
    table_match = re.search(r'<table class="diff".*?</table>', diff_html, re.DOTALL)
    if table_match:
        html += table_match.group(0)
    else:
        html += diff_html
    
    html += '</div></body></html>'
    
    return html

def compare_academic_texts(text1: str, text2: str, filename1: str, filename2: str) -> TextComparison:
    """Compare two academic texts and generate detailed comparison results."""
    # Split into paragraphs
    paragraphs1 = split_into_paragraphs(text1)
    paragraphs2 = split_into_paragraphs(text2)
    
    # Calculate overall similarity
    normalized_text1 = normalize_academic_text(text1)
    normalized_text2 = normalize_academic_text(text2)
    overall_similarity = calculate_similarity(normalized_text1, normalized_text2)
    
    # Calculate paragraph-level similarities
    para_similarities = []
    
    for para1 in paragraphs1:
        # Find best matching paragraph
        normalized_para1 = normalize_academic_text(para1)
        max_similarity = 0
        
        for para2 in paragraphs2:
            normalized_para2 = normalize_academic_text(para2)
            similarity = calculate_similarity(normalized_para1, normalized_para2)
            max_similarity = max(max_similarity, similarity)
        
        para_similarities.append(max_similarity)
    
    # Generate HTML diff
    html_diff = generate_html_diff(text1, text2, filename1, filename2, para_similarities)
    
    return TextComparison(
        similarity_ratio=overall_similarity,
        similarity_by_paragraph=para_similarities,
        html_diff=html_diff
    )

def compare_files(file_path1: str, file_path2: str, output_path: Optional[str] = None) -> TextComparison:
    """
    Compare two text files and generate HTML report showing similarities and differences.
    Optimized for academic texts with LaTeX commands and citations.
    
    Args:
        file_path1: Path to the first file
        file_path2: Path to the second file
        output_path: Optional path to save the HTML report
        
    Returns:
        TextComparison object containing similarity ratio, paragraph similarities, and HTML diff
    """
    path1 = Path(file_path1)
    path2 = Path(file_path2)
    
    if not path1.exists() or not path2.exists():
        raise FileNotFoundError(f"One or both files do not exist: {file_path1}, {file_path2}")
    
    with open(path1, 'r', encoding='utf-8', errors='replace') as f1, \
         open(path2, 'r', encoding='utf-8', errors='replace') as f2:
        text1 = f1.read()
        text2 = f2.read()
    
    comparison = compare_academic_texts(text1, text2, path1.name, path2.name)
    
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(comparison.html_diff)
        
        print(f"HTML comparison saved to {output_file}")
    
    return comparison

def compare_documents(doc1_path: str, doc2_path: str = None, output_path: str = None) -> None:
    """
    Compare two documents and generate an HTML report.
    If doc2_path is not provided, it will look for document2.txt.
    """
    # If only doc1_path is provided, assume it's a file name and look for both documents
    if doc2_path is None:
        # Check if it's already a full path
        if os.path.dirname(doc1_path):
            # It's a path, try to find document2.txt in the same directory
            base_dir = os.path.dirname(doc1_path)
            doc2_path = os.path.join(base_dir, "document2.txt")
        else:
            # It's just a filename, look in current directory
            doc1_path = os.path.join(os.getcwd(), doc1_path)
            doc2_path = os.path.join(os.getcwd(), "document2.txt")
    
    # Set a default output path if none provided
    if output_path is None:
        base_dir = os.path.dirname(doc1_path) if os.path.dirname(doc1_path) else os.getcwd()
        output_path = os.path.join(base_dir, "comparison_result.html")
    
    # Check if files exist
    if not os.path.exists(doc1_path):
        raise FileNotFoundError(f"File not found: {doc1_path}")
    
    if not os.path.exists(doc2_path):
        raise FileNotFoundError(f"File not found: {doc2_path}")
    
    # Perform comparison
    comparison = compare_files(doc1_path, doc2_path, output_path)
    
    print(f"Comparison completed:")
    print(f"  - Overall similarity: {comparison.similarity_ratio:.2%}")
    print(f"  - HTML report saved to: {output_path}")
    
    # Print paragraph-level similarities
    print("\nParagraph-level similarities:")
    for i, sim in enumerate(comparison.similarity_by_paragraph):
        print(f"  - Paragraph {i+1}: {sim:.2%}")
    
    return comparison

def main() -> int:
    """CLI interface for the academic plagiarism detector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect plagiarism in academic texts")
    parser.add_argument("file1", help="First file to compare")
    parser.add_argument("file2", nargs="?", default=None, help="Second file to compare (default: document2.txt)")
    parser.add_argument("-o", "--output", help="Output HTML file path", default=None)
    
    args = parser.parse_args()
    
    try:
        compare_documents(args.file1, args.file2, args.output)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())