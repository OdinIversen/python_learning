#!/usr/bin/env python
"""
Command-line interface for the plagiarism detector.
"""

import argparse
import sys
import os
from typing import List
import logging
from pathlib import Path

from plagiarism_detector import PlagiarismDetector


def setup_logger():
    """Configure logging for the CLI."""
    logger = logging.getLogger("plagiarism_detector")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Detect similarities and potential plagiarism between text documents",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("file1", 
                        help="Path to the first document file")
    
    parser.add_argument("file2", 
                        help="Path to the second document file")
    
    parser.add_argument("--title1", 
                        default=None,
                        help="Title for the first document (defaults to filename)")
    
    parser.add_argument("--title2", 
                        default=None,
                        help="Title for the second document (defaults to filename)")
    
    parser.add_argument("--threshold", 
                        type=float, 
                        default=0.7,
                        help="Similarity threshold (0.0 to 1.0)")
    
    parser.add_argument("--output-dir", 
                        default=os.path.join("personal_files", "plagiarism_results"),
                        help="Directory to save results")
    
    parser.add_argument("--formats", 
                        choices=["html", "json", "text", "summary", "chart", "heatmap", "gauge", "all"],
                        default=["html", "summary"],
                        nargs="+",
                        help="Output formats to generate")
    
    parser.add_argument("--verbose", "-v", 
                        action="store_true",
                        help="Enable verbose output")
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    # Setup logger
    logger = setup_logger()
    
    # Parse arguments
    args = parse_arguments()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose output enabled")
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set output formats
    output_formats = args.formats
    if "all" in output_formats:
        output_formats = ["html", "json", "text", "summary", "chart", "heatmap", "gauge"]
    
    logger.info(f"Output formats: {', '.join(output_formats)}")
    
    try:
        # Initialize detector
        logger.info(f"Initializing plagiarism detector with threshold: {args.threshold}")
        detector = PlagiarismDetector(threshold=args.threshold)
        
        # Analyze documents
        logger.info(f"Comparing documents:")
        logger.info(f"  Document 1: {args.file1}")
        logger.info(f"  Document 2: {args.file2}")
        
        result = detector.analyze(
            file_path1=args.file1,
            file_path2=args.file2,
            title1=args.title1,
            title2=args.title2,
            output_formats=output_formats
        )
        
        # Display results
        similarity = result["comparison"]["similarity_metrics"]["combined_similarity"]
        logger.info(f"Overall similarity: {similarity:.2f}")
        
        if similarity >= args.threshold:
            logger.warning(f"Similarity is above threshold ({args.threshold})!")
        else:
            logger.info(f"Similarity is below threshold ({args.threshold}).")
        
        # List generated reports
        logger.info("Generated reports:")
        for fmt, path in result["reports"].items():
            logger.info(f"  {fmt.upper()}: {path}")
        
        logger.info("Analysis complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())