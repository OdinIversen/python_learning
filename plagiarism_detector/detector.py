"""
Core Plagiarism Detection Module

This module contains the main PlagiarismDetector class.
"""

import difflib
from typing import Dict, List, Tuple, Set, Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from plagiarism_detector.text_processor import (
    ensure_nltk_resources,
    preprocess_text,
    get_sentences,
    tokenize_and_filter,
    get_ngrams
)
from plagiarism_detector.file_handler import load_document
from plagiarism_detector.visualizer import create_similarity_heatmap, create_similarity_gauge, create_bar_chart_comparison
from plagiarism_detector.report_generator import (
    generate_text_diff, 
    generate_json_report, 
    generate_html_report,
    generate_summary_report
)


class PlagiarismDetector:
    """
    A class for detecting similarities and potential plagiarism between text documents.
    """
    
    def __init__(self, threshold: float = 0.7) -> None:
        """
        Initialize the plagiarism detector with similarity threshold.
        
        Args:
            threshold: Similarity threshold (0.0 to 1.0)
        """
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 3),
            token_pattern=r'\b\w+\b',
            max_features=10000
        )
        
        # Ensure NLTK resources are available
        ensure_nltk_resources()
    
    def load_documents(self, file_path1: str, file_path2: str) -> Tuple[str, str]:
        """
        Load two documents for comparison.
        
        Args:
            file_path1: Path to the first document
            file_path2: Path to the second document
            
        Returns:
            Tuple containing the text content of both documents
        """
        text1 = load_document(file_path1)
        text2 = load_document(file_path2)
        
        return text1, text2
    
    def calculate_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Calculate similarity between two texts using multiple metrics.
        
        Args:
            text1: First text document
            text2: Second text document
            
        Returns:
            Dictionary of similarity scores and a combined score
        """
        # Preprocess texts
        processed_text1 = preprocess_text(text1)
        processed_text2 = preprocess_text(text2)
        
        # Calculate TF-IDF Cosine Similarity
        corpus = [processed_text1, processed_text2]
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Calculate Jaccard similarity for word overlap
        tokenized_text1 = set(tokenize_and_filter(processed_text1))
        tokenized_text2 = set(tokenize_and_filter(processed_text2))
        
        jaccard_sim = len(tokenized_text1.intersection(tokenized_text2)) / len(tokenized_text1.union(tokenized_text2)) if tokenized_text1 or tokenized_text2 else 0
        
        # Calculate sequence matcher for exact matches
        seq_matcher = difflib.SequenceMatcher(None, processed_text1, processed_text2)
        seq_sim = seq_matcher.ratio()
        
        # Calculate N-gram overlap (3-grams)
        ngrams1 = get_ngrams(processed_text1, 3)
        ngrams2 = get_ngrams(processed_text2, 3)
        ngram_sim = len(ngrams1.intersection(ngrams2)) / max(1, len(ngrams1.union(ngrams2)))
        
        # Combine metrics with weights
        combined_sim = (0.4 * cosine_sim + 0.2 * jaccard_sim + 0.2 * seq_sim + 0.2 * ngram_sim)
        
        return {
            "cosine_similarity": cosine_sim,
            "jaccard_similarity": jaccard_sim,
            "sequence_similarity": seq_sim,
            "ngram_similarity": ngram_sim,
            "combined_similarity": combined_sim
        }
    
    def find_shared_ngrams(self, text1: str, text2: str, n: int = 5) -> Dict[str, List[Tuple[int, List[int]]]]:
        """
        Find shared n-grams (phrases of n words) between two texts.
        
        Args:
            text1: First text document
            text2: Second text document
            n: Size of n-gram (number of words)
            
        Returns:
            Dictionary of shared n-grams with their positions in both texts
        """
        # Preprocess texts
        processed_text1 = preprocess_text(text1)
        processed_text2 = preprocess_text(text2)
        
        # Tokenize
        words1 = tokenize_and_filter(processed_text1, remove_stopwords=False)
        words2 = tokenize_and_filter(processed_text2, remove_stopwords=False)
        
        # Generate n-grams
        ngrams1 = [' '.join(words1[i:i+n]) for i in range(len(words1) - n + 1)]
        ngrams2 = [' '.join(words2[i:i+n]) for i in range(len(words2) - n + 1)]
        
        # Find shared n-grams
        shared_ngrams = {}
        
        for i, ngram in enumerate(ngrams1):
            # Skip very short n-grams
            if len(ngram.strip()) < 10 or ngram.count(' ') < n-1:
                continue
                
            # Check if this n-gram appears in the second document
            if ngram in ngrams2:
                positions = [j for j, ng in enumerate(ngrams2) if ng == ngram]
                if ngram not in shared_ngrams:
                    shared_ngrams[ngram] = []
                shared_ngrams[ngram].append((i, positions))
        
        # Sort by significance
        sorted_ngrams = dict(sorted(
            shared_ngrams.items(),
            key=lambda x: (
                sum(len(pos) for _, pos in x[1]),  # Total occurrences
                len(x[0]),                         # Length of phrase
                x[0].count(' ')                    # Number of spaces (words)
            ),
            reverse=True
        ))
        
        return sorted_ngrams
    
    def compare_documents(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Compare two documents and calculate various similarity metrics.
        
        Args:
            text1: First text document
            text2: Second text document
            
        Returns:
            Dictionary with comprehensive comparison results
        """
        # Calculate similarity
        similarity_metrics = self.calculate_similarity(text1, text2)
        
        # Find shared n-grams
        shared_ngrams = self.find_shared_ngrams(text1, text2)
        
        # Determine if similarity is above threshold
        is_similar = similarity_metrics["combined_similarity"] >= self.threshold
        
        return {
            "similarity_metrics": similarity_metrics,
            "shared_ngrams": shared_ngrams,
            "is_similar": is_similar,
            "text1_stats": {
                "word_count": len(text1.split()),
                "char_count": len(text1),
                "sentence_count": len(get_sentences(preprocess_text(text1)))
            },
            "text2_stats": {
                "word_count": len(text2.split()),
                "char_count": len(text2),
                "sentence_count": len(get_sentences(preprocess_text(text2)))
            }
        }
    
    def generate_reports(self, text1: str, text2: str, comparison_result: Dict[str, Any],
                       title1: str = "Document 1", title2: str = "Document 2", 
                       output_formats: List[str] = ["html"]) -> Dict[str, str]:
        """
        Generate various report formats based on comparison results.
        
        Args:
            text1: First text document
            text2: Second text document
            comparison_result: Results from compare_documents()
            title1: Title for the first document
            title2: Title for the second document
            output_formats: List of desired output formats (html, json, text, summary)
            
        Returns:
            Dictionary mapping format names to output file paths
        """
        similarity_metrics = comparison_result["similarity_metrics"]
        shared_ngrams = comparison_result["shared_ngrams"]
        outputs = {}
        
        if "html" in output_formats:
            html_path = generate_html_report(text1, text2, similarity_metrics, shared_ngrams, 
                                           title1=title1, title2=title2)
            outputs["html"] = html_path
            
        if "json" in output_formats:
            json_path = generate_json_report(text1, text2, similarity_metrics, shared_ngrams,
                                           title1=title1, title2=title2)
            outputs["json"] = json_path
            
        if "text" in output_formats:
            text_path = generate_text_diff(text1, text2)
            outputs["text"] = text_path
            
        if "summary" in output_formats:
            summary_path = generate_summary_report(text1, text2, similarity_metrics, shared_ngrams,
                                                 title1=title1, title2=title2)
            outputs["summary"] = summary_path
            
        if "chart" in output_formats:
            chart_path = create_bar_chart_comparison(similarity_metrics)
            outputs["chart"] = chart_path
            
        if "heatmap" in output_formats:
            heatmap_path = create_similarity_heatmap(text1, text2)
            outputs["heatmap"] = heatmap_path
            
        if "gauge" in output_formats:
            gauge_path = create_similarity_gauge(similarity_metrics["combined_similarity"])
            outputs["gauge"] = gauge_path
            
        return outputs
    
    def analyze(self, file_path1: str, file_path2: str, title1: str = None, title2: str = None, 
              output_formats: List[str] = ["html", "summary"]) -> Dict[str, Any]:
        """
        Load, compare, and generate reports for two documents in a single call.
        
        Args:
            file_path1: Path to the first document
            file_path2: Path to the second document
            title1: Title for the first document (defaults to filename)
            title2: Title for the second document (defaults to filename)
            output_formats: List of desired output formats
            
        Returns:
            Dictionary with comparison results and paths to generated reports
        """
        # Load documents
        text1, text2 = self.load_documents(file_path1, file_path2)
        
        # Set default titles to filenames if not provided
        if title1 is None:
            title1 = file_path1.split("/")[-1]
        if title2 is None:
            title2 = file_path2.split("/")[-1]
        
        # Compare documents
        comparison_result = self.compare_documents(text1, text2)
        
        # Generate reports
        report_paths = self.generate_reports(text1, text2, comparison_result, title1, title2, output_formats)
        
        # Combine results
        result = {
            "comparison": comparison_result,
            "reports": report_paths
        }
        
        return result