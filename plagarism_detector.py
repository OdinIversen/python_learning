import argparse
import difflib
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
from pathlib import Path


class PlagiarismDetector:
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
            token_pattern=r'\b\w+\b'
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean the text by removing extra whitespace and normalizing."""
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.lower().strip()
        return text
    
    def _get_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts using TF-IDF.
        
        Args:
            text1: First text document
            text2: Second text document
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        corpus = [text1, text2]
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    
    def find_shared_ngrams(self, text1: str, text2: str, n: int = 5) -> Dict[str, List[int]]:
        """
        Find shared n-grams (phrases of n words) between the two texts.
        
        Args:
            text1: First text document
            text2: Second text document
            n: Size of n-gram (number of words)
            
        Returns:
            Dictionary of shared n-grams with their positions in both texts
        """
        words1 = text1.split()
        words2 = text2.split()
        
        ngrams1 = [' '.join(words1[i:i+n]) for i in range(len(words1) - n + 1)]
        ngrams2 = [' '.join(words2[i:i+n]) for i in range(len(words2) - n + 1)]
        
        shared_ngrams = {}
        
        for i, ngram in enumerate(ngrams1):
            if ngram in ngrams2:
                positions = [j for j, ng in enumerate(ngrams2) if ng == ngram]
                if ngram not in shared_ngrams:
                    shared_ngrams[ngram] = []
                shared_ngrams[ngram].append((i, positions))
        
        return shared_ngrams
    
    def generate_diff_html(self, text1: str, text2: str, output_file: str) -> None:
        """
        Generate an HTML file showing differences between the texts.
        
        Args:
            text1: First text document
            text2: Second text document
            output_file: Path to save the HTML output
        """
        d = difflib.HtmlDiff()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(d.make_file(text1.splitlines(), text2.splitlines(), 
                               "Document 1", "Document 2"))
    
    def plot_similarity_heatmap(self, text1: str, text2: str, output_file: Optional[str] = None) -> None:
        """
        Create and display a heatmap showing sentence-level similarities.
        
        Args:
            text1: First text document
            text2: Second text document
            output_file: Optional path to save the heatmap image
        """
        sentences1 = self._get_sentences(text1)
        sentences2 = self._get_sentences(text2)
        
        similarity_matrix = np.zeros((len(sentences1), len(sentences2)))
        
        for i, sent1 in enumerate(sentences1):
            for j, sent2 in enumerate(sentences2):
                if sent1 and sent2:  # Ensure sentences are not empty
                    similarity_matrix[i, j] = self.calculate_similarity(sent1, sent2)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            similarity_matrix, 
            annot=False, 
            cmap="YlOrRd", 
            xticklabels=[f"S{i+1}" for i in range(len(sentences2))], 
            yticklabels=[f"S{i+1}" for i in range(len(sentences1))]
        )
        plt.title("Sentence-level Similarity Heatmap")
        plt.xlabel("Document 2 Sentences")
        plt.ylabel("Document 1 Sentences")
        
        if output_file:
            plt.savefig(output_file, bbox_inches='tight')
            print(f"Heatmap saved to {output_file}")
        else:
            plt.show()
        plt.close()
    
    def generate_latex_diff(self, text1: str, text2: str, output_file: str) -> None:
        """
        Generate LaTeX code to visualize differences between texts.
        
        Args:
            text1: First text document
            text2: Second text document
            output_file: Path to save the LaTeX output
        """
        # Split the text into sentences for more granular comparison
        sentences1 = self._get_sentences(text1)
        sentences2 = self._get_sentences(text2)
        
        # Find matching and differing sentences
        matcher = difflib.SequenceMatcher(None, sentences1, sentences2)
        
        # LaTeX preamble
        latex_content = [
            r"\documentclass{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage{xcolor}",
            r"\usepackage{soul}",
            r"\usepackage{geometry}",
            r"\geometry{a4paper, margin=1in}",
            r"\title{Plagiarism Detection Report}",
            r"\author{Automated Plagiarism Detector}",
            r"\date{\today}",
            r"\begin{document}",
            r"\maketitle",
            r"\section{Document Comparison}",
            r"\subsection{Overall Similarity}",
            f"Overall similarity score: {self.calculate_similarity(text1, text2):.2f}",
            r"",
            r"\subsection{Document 1}",
            r"\begin{itemize}",
            r"\item \textbf{Original text:} Text in black",
            r"\item \textbf{Similar content:} \colorbox{yellow}{Highlighted in yellow}",
            r"\end{itemize}",
            r"",
        ]
        
        # Process document 1
        current_pos = 0
        doc1_content = []
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                # Matched content
                for sentence in sentences1[i1:i2]:
                    doc1_content.append(f"\\colorbox{{yellow}}{{{sentence}}} ")
            else:
                # Content unique to document 1
                for sentence in sentences1[i1:i2]:
                    doc1_content.append(f"{sentence} ")
        
        latex_content.append("\\begin{quotation}")
        latex_content.append(" ".join(doc1_content))
        latex_content.append("\\end{quotation}")
        
        # Document 2
        latex_content.extend([
            r"",
            r"\subsection{Document 2}",
            r"\begin{itemize}",
            r"\item \textbf{Original text:} Text in black",
            r"\item \textbf{Similar content:} \colorbox{yellow}{Highlighted in yellow}",
            r"\end{itemize}",
            r"",
        ])
        
        # Process document 2
        current_pos = 0
        doc2_content = []
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                # Matched content
                for sentence in sentences2[j1:j2]:
                    doc2_content.append(f"\\colorbox{{yellow}}{{{sentence}}} ")
            else:
                # Content unique to document 2
                for sentence in sentences2[j1:j2]:
                    doc2_content.append(f"{sentence} ")
        
        latex_content.append("\\begin{quotation}")
        latex_content.append(" ".join(doc2_content))
        latex_content.append("\\end{quotation}")
        
        # Shared n-grams section
        shared_ngrams = self.find_shared_ngrams(text1, text2)
        if shared_ngrams:
            latex_content.extend([
                r"",
                r"\section{Shared Phrases}",
                r"The following phrases (5-word sequences) appear in both documents:",
                r"\begin{itemize}",
            ])
            
            for ngram in list(shared_ngrams.keys())[:20]:  # Limit to top 20 for readability
                latex_content.append(f"\\item \"{ngram}\"")
            
            if len(shared_ngrams) > 20:
                latex_content.append(f"\\item ... and {len(shared_ngrams) - 20} more")
                
            latex_content.append(r"\end{itemize}")
        
        # Close the document
        latex_content.append(r"\end{document}")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(latex_content))
        
        print(f"LaTeX report saved to {output_file}")
    
    def analyze(self, file1: str, file2: str, output_dir: str = "results") -> None:
        """
        Analyze two documents for plagiarism and generate reports.
        
        Args:
            file1: Path to first document
            file2: Path to second document
            output_dir: Directory to save analysis results
        """
        with open(file1, 'r', encoding='utf-8') as f:
            text1 = self._preprocess_text(f.read())
        
        with open(file2, 'r', encoding='utf-8') as f:
            text2 = self._preprocess_text(f.read())
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True, parents=True)
        
        # Calculate similarity
        similarity = self.calculate_similarity(text1, text2)
        result_summary = [
            f"Plagiarism Detection Report",
            f"========================",
            f"",
            f"Document 1: {os.path.basename(file1)}",
            f"Document 2: {os.path.basename(file2)}",
            f"",
            f"Overall similarity score: {similarity:.2f}",
            f"",
            f"Interpretation:",
        ]
        
        if similarity >= 0.8:
            result_summary.append("HIGH SIMILARITY - Likely plagiarism or legitimate reuse")
        elif similarity >= 0.5:
            result_summary.append("MODERATE SIMILARITY - Possible partial plagiarism or similar topic")
        else:
            result_summary.append("LOW SIMILARITY - Probably different content")
        
        # Save results
        with open(os.path.join(output_dir, "similarity_report.txt"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(result_summary))
        
        base_name = f"{Path(file1).stem}_vs_{Path(file2).stem}"
        self.generate_diff_html(text1, text2, os.path.join(output_dir, f"{base_name}_diff.html"))
        self.plot_similarity_heatmap(text1, text2, os.path.join(output_dir, f"{base_name}_heatmap.png"))
        self.generate_latex_diff(text1, text2, os.path.join(output_dir, f"{base_name}_report.tex"))
        
        print(f"Analysis complete. Results saved to {output_dir}/")
        print(f"Overall similarity: {similarity:.2f}")


def main() -> None:
    # Hardcoded filenames in personal_files folder
    file1 = "personal_files/document1.txt"
    file2 = "personal_files/document2.txt"
    output_dir = "personal_files/plagiarism_results"
    threshold = 0.7
    
    detector = PlagiarismDetector(threshold=threshold)
    detector.analyze(file1, file2, output_dir)
    print(f"Analysis complete. Results saved to {output_dir}/")


if __name__ == "__main__":
    main()