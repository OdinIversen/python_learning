#!/usr/bin/env python3
"""
Simple script to compare two academic text documents from the personal_files directory.
"""
from academic_plagiarism_detector import compare_documents
import sys
import os
from pathlib import Path

def main() -> int:
    try:
        # Setup paths - using personal_files directory
        personal_dir = Path("personal_files")
        
        # Check if personal_files directory exists
        if not personal_dir.exists():
            print(f"Error: personal_files directory not found in {os.getcwd()}")
            return 1
        
        # Document paths within personal_files
        doc1_path = personal_dir / "document1.txt"
        
        # Check if document1.txt exists in personal_files
        if not doc1_path.exists():
            print(f"Error: Could not find document1.txt in the personal_files directory.")
            return 1
        
        # Parse optional document2 path
        if len(sys.argv) > 1:
            doc2_path = personal_dir / sys.argv[1]
        else:
            doc2_path = personal_dir / "document2.txt"
        
        # Check if document2 exists
        if not doc2_path.exists():
            print(f"Error: Could not find {doc2_path.name} in the personal_files directory.")
            return 1
        
        # Set output path in personal_files directory
        output_filename = sys.argv[2] if len(sys.argv) > 2 else "comparison_result.html"
        output_path = personal_dir / output_filename
        
        print(f"Comparing: {doc1_path.name} with {doc2_path.name}")
        print(f"Output will be saved to: {output_path}")
        
        # Run the comparison
        compare_documents(str(doc1_path), str(doc2_path), str(output_path))
        
        print(f"\nComparison complete! HTML report saved to: {output_path}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())