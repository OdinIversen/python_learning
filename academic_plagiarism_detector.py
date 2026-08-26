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

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words and punctuation for more precise diffing.
    Preserves whitespace as separate tokens to maintain formatting.
    """
    # This pattern separates words, punctuation, and whitespace
    pattern = r'(\s+|[^\w\s]+|\w+)'
    return re.findall(pattern, text)

def highlight_differences(tokens1: List[str], tokens2: List[str]) -> Tuple[str, str]:
    """
    Compare two lists of tokens and return HTML with differences highlighted.
    """
    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    
    # Create HTML for both texts with highlighted differences
    html1 = []
    html2 = []
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            # Same text in both documents
            segment1 = ''.join(tokens1[i1:i2])
            segment2 = ''.join(tokens2[j1:j2])
            html1.append(f'<span class="identical">{segment1}</span>')
            html2.append(f'<span class="identical">{segment2}</span>')
        elif op == 'delete':
            # Text only in document 1
            segment = ''.join(tokens1[i1:i2])
            html1.append(f'<span class="deleted">{segment}</span>')
        elif op == 'insert':
            # Text only in document 2
            segment = ''.join(tokens2[j1:j2])
            html2.append(f'<span class="inserted">{segment}</span>')
        elif op == 'replace':
            # Different text in both documents
            segment1 = ''.join(tokens1[i1:i2])
            segment2 = ''.join(tokens2[j1:j2])
            html1.append(f'<span class="changed">{segment1}</span>')
            html2.append(f'<span class="changed">{segment2}</span>')
    
    return ''.join(html1), ''.join(html2)

def generate_html_diff(text1: str, text2: str, filename1: str, filename2: str) -> str:
    """
    Generate HTML showing differences between two texts with word-level highlights.
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
        .deleted {
            background-color: #FF9E9E;
            text-decoration: line-through;
        }
        .inserted {
            background-color: #A1FFA1;
        }
        .changed {
            background-color: #FFEE75;
        }
        .identical {
            background-color: #E0E0FF;
        }
        .color-legend {
            margin-top: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f8f8f8;
        }
        .color-legend h2 {
            margin-top: 0;
        }
        .color-legend ul {
            list-style-type: none;
            padding-left: 0;
        }
        .color-legend li {
            margin: 10px 0;
            display: flex;
            align-items: center;
        }
        .legend-box {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #aaa;
        }
        .legend-box.identical {
            background-color: #E0E0FF;
        }
        .legend-box.deleted {
            background-color: #FF9E9E;
        }
        .legend-box.inserted {
            background-color: #A1FFA1;
        }
        .legend-box.changed {
            background-color: #FFEE75;
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

    # Add side-by-side comparison with word-level highlighting
    html += '<div class="container">'
    
    # Create lists to store the HTML for each paragraph
    doc1_paragraphs_html = []
    doc2_paragraphs_html = []
    
    # Find matching paragraphs and highlight differences
    max_paragraphs = max(len(paragraphs1), len(paragraphs2))
    
    for i in range(max_paragraphs):
        if i < len(paragraphs1) and i < len(paragraphs2):
            # Both documents have a paragraph at this position
            para1 = paragraphs1[i]
            para2 = paragraphs2[i]
            
            # Tokenize paragraphs for word-level diff
            tokens1 = tokenize_text(para1)
            tokens2 = tokenize_text(para2)
            
            # Get highlighted versions
            highlighted1, highlighted2 = highlight_differences(tokens1, tokens2)
            
            doc1_paragraphs_html.append(f'<div class="paragraph">{highlighted1}</div>')
            doc2_paragraphs_html.append(f'<div class="paragraph">{highlighted2}</div>')
        elif i < len(paragraphs1):
            # Only document 1 has a paragraph at this position
            para1 = paragraphs1[i]
            doc1_paragraphs_html.append(f'<div class="paragraph"><span class="deleted">{para1}</span></div>')
            doc2_paragraphs_html.append(f'<div class="paragraph"></div>')
        else:
            # Only document 2 has a paragraph at this position
            para2 = paragraphs2[i]
            doc1_paragraphs_html.append(f'<div class="paragraph"></div>')
            doc2_paragraphs_html.append(f'<div class="paragraph"><span class="inserted">{para2}</span></div>')
    
    # Document 1 column
    html += f'<div class="column"><div class="document-title">Document 1: {filename1}</div>'
    html += ''.join(doc1_paragraphs_html)
    html += '</div>'
    
    # Document 2 column
    html += f'<div class="column"><div class="document-title">Document 2: {filename2}</div>'
    html += ''.join(doc2_paragraphs_html)
    html += '</div></div>'
    
    # Add legend for color meanings
    html += '''
    <div class="color-legend">
        <h2>Color Legend</h2>
        <ul>
            <li><span class="legend-box identical"></span> <strong>Identical text</strong> - Text that appears in both documents</li>
            <li><span class="legend-box deleted"></span> <strong>Deleted text</strong> - Text that only appears in Document 1</li>
            <li><span class="legend-box inserted"></span> <strong>Added text</strong> - Text that only appears in Document 2</li>
            <li><span class="legend-box changed"></span> <strong>Modified text</strong> - Text that appears in both documents but with differences</li>
        </ul>
    </div>'''
    
    html += '</div></body></html>'
    
    return html

def compare_academic_texts(text1: str, text2: str, filename1: str, filename2: str) -> TextComparison:
    """Compare two academic texts and generate detailed comparison results with word-level highlighting."""
    # Calculate overall similarity
    normalized_text1 = normalize_academic_text(text1)
    normalized_text2 = normalize_academic_text(text2)
    overall_similarity = calculate_similarity(normalized_text1, normalized_text2)
    
    # Generate HTML diff with word-level highlighting
    html_diff = generate_html_diff(text1, text2, filename1, filename2)
    
    return TextComparison(
        similarity_ratio=overall_similarity,
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
        TextComparison object containing similarity ratio and HTML diff
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