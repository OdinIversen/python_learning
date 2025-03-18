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
            token_pattern=r'\b\w+\b',
            max_features=10000  # Limit features for performance
        )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess academic text, preserving paragraph structure.
        Handles LaTeX citations and commands properly.
        """
        # Replace LaTeX citations with placeholders to reduce their impact on similarity
        text = re.sub(r'\\parencite\{[^}]+\}', '[CITATION]', text)
        text = re.sub(r'\\textcite\{[^}]+\}', '[CITATION]', text)
        text = re.sub(r'\\cite\{[^}]+\}', '[CITATION]', text)
        
        # Handle LaTeX quotes
        text = re.sub(r"''", '"', text)
        
        # Normalize whitespace but preserve paragraph breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        # Remove section headers (e.g., "Journal paper:", "Masters thesis:")
        text = re.sub(r'^[^:]+:\s*', '', text)
        
        return text
    
    def _get_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences, handling academic text with LaTeX commands.
        """
        # First handle LaTeX period notations that shouldn't be split
        text = re.sub(r'\.\s*\\', '.\\', text)
        
        # Split by common sentence terminators, but avoid splitting citations
        # This is a simplified approach - complete LaTeX parsing would be more complex
        potential_sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        
        # Clean up the sentences and remove empty ones
        sentences = [s.strip() for s in potential_sentences if s.strip()]
        return sentences
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using multiple metrics and return a combined score.
        
        Args:
            text1: First text document
            text2: Second text document
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # 1. TF-IDF Cosine Similarity
        corpus = [text1, text2]
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # 2. Jaccard similarity for word overlap
        words1 = set(text1.split())
        words2 = set(text2.split())
        jaccard_sim = len(words1.intersection(words2)) / len(words1.union(words2)) if words1 or words2 else 0
        
        # 3. Sequence matcher for exact matches
        seq_matcher = difflib.SequenceMatcher(None, text1, text2)
        seq_sim = seq_matcher.ratio()
        
        # 4. N-gram overlap
        def get_ngrams(text, n):
            words = text.split()
            return set(' '.join(words[i:i+n]) for i in range(len(words) - n + 1))
            
        # Calculate overlap of 3-grams (phrases of 3 words)
        ngrams1 = get_ngrams(text1, 3)
        ngrams2 = get_ngrams(text2, 3)
        ngram_sim = len(ngrams1.intersection(ngrams2)) / max(1, len(ngrams1.union(ngrams2)))
        
        # Combine metrics with weights
        combined_sim = (0.4 * cosine_sim + 0.2 * jaccard_sim + 0.2 * seq_sim + 0.2 * ngram_sim)
        
        return combined_sim
    
    def find_shared_ngrams(self, text1: str, text2: str, n: int = 5) -> Dict[str, List[Tuple[int, List[int]]]]:
        """
        Find shared n-grams (phrases of n words) between the two texts.
        Enhanced to handle academic text with specialized citation patterns.
        
        Args:
            text1: First text document
            text2: Second text document
            n: Size of n-gram (number of words)
            
        Returns:
            Dictionary of shared n-grams with their positions in both texts
        """
        # Clean text to better handle citations and academic writing
        def clean_for_ngrams(text):
            # Replace citation commands with placeholders to reduce their impact
            text = re.sub(r'\\parencite\{[^}]+\}', '[CITE]', text)
            text = re.sub(r'\\textcite\{[^}]+\}', '[CITE]', text)
            text = re.sub(r'\\cite\{[^}]+\}', '[CITE]', text)
            # Handle quotes and other LaTeX formatting
            text = re.sub(r"''", '"', text)
            text = re.sub(r'`', "'", text)
            return text
        
        # Clean the texts
        clean_text1 = clean_for_ngrams(text1)
        clean_text2 = clean_for_ngrams(text2)
        
        # Split into words
        words1 = clean_text1.split()
        words2 = clean_text2.split()
        
        # Generate n-grams
        ngrams1 = [' '.join(words1[i:i+n]) for i in range(len(words1) - n + 1)]
        ngrams2 = [' '.join(words2[i:i+n]) for i in range(len(words2) - n + 1)]
        
        # Find shared n-grams
        shared_ngrams = {}
        
        for i, ngram in enumerate(ngrams1):
            # Skip very short n-grams or those consisting mostly of common words
            if len(ngram.strip()) < 10 or ngram.count(' ') < n-1:
                continue
                
            # Check if this n-gram appears in the second document
            if ngram in ngrams2:
                positions = [j for j, ng in enumerate(ngrams2) if ng == ngram]
                if ngram not in shared_ngrams:
                    shared_ngrams[ngram] = []
                shared_ngrams[ngram].append((i, positions))
        
        # Sort shared n-grams by frequency and significance
        # Give higher weight to longer, more meaningful phrases
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
    
    def plot_similarity_heatmap(self, text1: str, text2: str, output_file: Optional[str] = None) -> None:
        """
        Create and display a heatmap showing sentence-level similarities.
        Enhanced for academic text comparison.
        
        Args:
            text1: First text document
            text2: Second text document
            output_file: Optional path to save the heatmap image
        """
        # Get sentences, limiting to a reasonable number for visualization
        sentences1 = self._get_sentences(text1)[:20]  # Limit to 20 sentences for legibility
        sentences2 = self._get_sentences(text2)[:20]
        
        # Create similarity matrix
        similarity_matrix = np.zeros((len(sentences1), len(sentences2)))
        
        # Compute similarity scores using difflib for sentence-level comparison
        # This is better for detecting similar academic phrasing
        for i, sent1 in enumerate(sentences1):
            for j, sent2 in enumerate(sentences2):
                if sent1 and sent2:  # Ensure sentences are not empty
                    # Use SequenceMatcher for more granular similarity
                    similarity_matrix[i, j] = difflib.SequenceMatcher(None, sent1, sent2).ratio()
        
        # Create a more detailed heatmap
        plt.figure(figsize=(14, 10))
        
        # Use a different colormap that better highlights variations
        ax = sns.heatmap(
            similarity_matrix, 
            annot=False,  # No annotations for cleaner look
            cmap="YlGnBu",  # Blue-based colormap for academic context
            xticklabels=[f"S{i+1}" for i in range(len(sentences2))], 
            yticklabels=[f"S{i+1}" for i in range(len(sentences1))],
            vmin=0,
            vmax=1,
            cbar_kws={'label': 'Similarity Score'}
        )
        
        # Improve visualization
        plt.title("Academic Text Similarity Heatmap (Sentence Level)", fontsize=16)
        plt.xlabel("Document 2 (Journal) Sentences", fontsize=12)
        plt.ylabel("Document 1 (Thesis) Sentences", fontsize=12)
        
        # Adjust to make text more legible
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(fontsize=9)
        
        # Tight layout to maximize visualization space
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, bbox_inches='tight', dpi=150)  # Higher DPI for better quality
            print(f"Heatmap saved to {output_file}")
        else:
            plt.show()
        plt.close()
    
    def generate_diff_html(self, text1: str, text2: str, output_file: str) -> None:
        """
        Generate a comprehensive HTML report showing similarities and differences between texts.
        
        Args:
            text1: First text document
            text2: Second text document
            output_file: Path to save the HTML output
        """
        # Calculate overall similarity
        similarity = self.calculate_similarity(text1, text2)
        
        # Split the texts into paragraphs for better readability
        # For academic text, we need proper paragraph splitting
        paragraphs1 = [p.strip() for p in text1.split('\n\n') if p.strip()]
        paragraphs2 = [p.strip() for p in text2.split('\n\n') if p.strip()]
        
        # Get sentences for sentence-level comparison
        sentences1 = self._get_sentences(text1)
        sentences2 = self._get_sentences(text2)
        
        # Find shared n-grams
        shared_ngrams = self.find_shared_ngrams(text1, text2)
        
        # Create HTML with proper formatting
        html_output = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>Academic Text Similarity Analysis</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }',
            '        .diff-container { display: flex; flex-direction: column; gap: 20px; }',
            '        .diff-section { display: flex; gap: 20px; }',
            '        .doc { flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }',
            '        h1, h2, h3 { color: #333; }',
            '        .highlight { background-color: #ffff99; }',
            '        .strong-highlight { background-color: #ffcc00; font-weight: bold; }',
            '        .similar { color: #008800; }',
            '        .different { color: #cc0000; }',
            '        .moderate { color: #ff6600; }',
            '        .stats { background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }',
            '        .paragraph { margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }',
            '        .similarity-score { font-weight: bold; font-size: 1.2em; }',
            '        .summary { border-left: 4px solid #333; padding-left: 15px; margin: 20px 0; }',
            '        .tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #ddd; }',
            '        .tab { padding: 10px 20px; cursor: pointer; border: 1px solid #ddd; background: #f1f1f1; border-bottom: none; margin-right: 5px; border-radius: 5px 5px 0 0; }',
            '        .tab.active { background: #fff; border-bottom: 1px solid #fff; position: relative; top: 1px; }',
            '        .tab-content { display: none; }',
            '        .tab-content.active { display: block; }',
            '        .heatmap { text-align: center; margin: 20px 0; }',
            '        .heatmap img { max-width: 100%; height: auto; border: 1px solid #ddd; }',
            '        table { width: 100%; border-collapse: collapse; margin: 20px 0; }',
            '        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '        th { background-color: #f2f2f2; }',
            '        tr:nth-child(even) { background-color: #f9f9f9; }',
            '        .citation { color: #555; font-style: italic; }',
            '        .header { font-weight: bold; color: #444; margin-bottom: 10px; }',
            '        .side-by-side { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }',
            '        .sentence-comparison { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 15px; }',
            '        .sentence-pair { display: flex; border-bottom: 1px dashed #ccc; padding-bottom: 10px; margin-bottom: 10px; }',
            '        .sentence-1, .sentence-2 { flex: 1; padding: 5px; }',
            '        .match-score { font-size: 0.9em; text-align: center; background: #eee; padding: 2px 5px; border-radius: 3px; margin: 0 5px; }',
            '        .key-phrase { background-color: #e6f3ff; padding: 2px 4px; border-radius: 3px; }',
            '    </style>',
            '    <script>',
            '        function openTab(evt, tabName) {',
            '            var i, tabcontent, tablinks;',
            '            tabcontent = document.getElementsByClassName("tab-content");',
            '            for (i = 0; i < tabcontent.length; i++) {',
            '                tabcontent[i].style.display = "none";',
            '            }',
            '            tablinks = document.getElementsByClassName("tab");',
            '            for (i = 0; i < tablinks.length; i++) {',
            '                tablinks[i].className = tablinks[i].className.replace(" active", "");',
            '            }',
            '            document.getElementById(tabName).style.display = "block";',
            '            evt.currentTarget.className += " active";',
            '        }',
            '        window.onload = function() {',
            '            document.getElementById("default-tab").click();',
            '        };',
            '    </script>',
            '</head>',
            '<body>',
            '    <h1>Academic Text Similarity Analysis</h1>',
            '    <div class="stats">',
            f'        <p><span class="similarity-score">Overall Similarity Score: {similarity:.2f}</span></p>',
            '        <div class="summary">',
        ]
        
        # Add interpretation
        if similarity >= 0.8:
            html_output.append('            <p class="similar"><strong>HIGH SIMILARITY</strong> - Significant overlap in content and wording</p>')
        elif similarity >= 0.5:
            html_output.append('            <p class="moderate"><strong>MODERATE SIMILARITY</strong> - Similar ideas with different expressions</p>')
        else:
            html_output.append('            <p class="different"><strong>LOW SIMILARITY</strong> - Substantially different texts</p>')
        
        html_output.append('        </div>')
        html_output.append('    </div>')
        
        # Add tabs for different views
        html_output.extend([
            '    <div class="tabs">',
            '        <button class="tab active" id="default-tab" onclick="openTab(event, \'paragraph-view\')">Paragraph Comparison</button>',
            '        <button class="tab" onclick="openTab(event, \'sentence-view\')">Sentence Analysis</button>',
            '        <button class="tab" onclick="openTab(event, \'ngram-view\')">Shared Phrases</button>',
            '        <button class="tab" onclick="openTab(event, \'heatmap-view\')">Similarity Heatmap</button>',
            '        <button class="tab" onclick="openTab(event, \'stats-view\')">Statistics</button>',
            '    </div>',
            '',
            '    <!-- Paragraph comparison tab -->',
            '    <div id="paragraph-view" class="tab-content active">',
            '        <h2>Paragraph-by-Paragraph Comparison</h2>',
            '        <div class="diff-container">'
        ])
        
        # Process all paragraphs
        para_similarities = []
        for i, paragraph1 in enumerate(paragraphs1):
            html_output.append('        <div class="diff-section">')
            html_output.append(f'            <div class="doc"><h3>Document 1 - Paragraph {i+1}</h3>')
            
            # Find the best matching paragraph in document 2
            best_match_idx = -1
            best_ratio = 0
            
            for j, paragraph2 in enumerate(paragraphs2):
                ratio = difflib.SequenceMatcher(None, paragraph1, paragraph2).ratio()
                if ratio > best_ratio and ratio > 0.3:  # Lower threshold for academic text
                    best_ratio = ratio
                    best_match_idx = j
            
            para_similarities.append(best_ratio)
            
            # Format paragraph 1
            if best_match_idx >= 0:
                # Highlight similar parts
                s = difflib.SequenceMatcher(None, paragraph1, paragraphs2[best_match_idx])
                paragraph1_html = []
                
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == 'equal' and i2-i1 > 5:  # Only highlight substantial matches
                        paragraph1_html.append(f'<span class="highlight">{paragraph1[i1:i2]}</span>')
                    else:
                        paragraph1_html.append(paragraph1[i1:i2])
                
                html_output.append(f'            <div class="paragraph">{"".join(paragraph1_html)}</div>')
                html_output.append(f'            <p class="similar">Similarity to Document 2, Paragraph {best_match_idx+1}: {best_ratio:.2f}</p>')
            else:
                html_output.append(f'            <div class="paragraph">{paragraph1}</div>')
                html_output.append('            <p class="different">No similar paragraph found in Document 2</p>')
            
            html_output.append('            </div>')
            
            # Show the matching paragraph from document 2 if one was found
            if best_match_idx >= 0:
                html_output.append(f'            <div class="doc"><h3>Document 2 - Paragraph {best_match_idx+1}</h3>')
                
                # Format paragraph 2
                s = difflib.SequenceMatcher(None, paragraph1, paragraphs2[best_match_idx])
                paragraph2_html = []
                
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == 'equal' and i2-i1 > 5:  # Only highlight substantial matches
                        paragraph2_html.append(f'<span class="highlight">{paragraphs2[best_match_idx][j1:j2]}</span>')
                    else:
                        paragraph2_html.append(paragraphs2[best_match_idx][j1:j2])
                
                html_output.append(f'            <div class="paragraph">{"".join(paragraph2_html)}</div>')
                html_output.append('            </div>')
            else:
                html_output.append('            <div class="doc"><h3>Document 2</h3>')
                html_output.append('            <p class="different">No matching paragraph</p>')
                html_output.append('            </div>')
            
            html_output.append('        </div>')
        
        # Close the paragraph view
        html_output.append('        </div>')
        html_output.append('    </div>')
        
        # Sentence Analysis Tab
        html_output.extend([
            '    <!-- Sentence comparison tab -->',
            '    <div id="sentence-view" class="tab-content">',
            '        <h2>Sentence-Level Analysis</h2>',
            '        <p>This section compares individual sentences across both documents to identify similar content expressed differently.</p>',
            '        <div class="sentence-comparison">'
        ])
        
        # Create a matrix of sentence similarities
        sentence_sim_matrix = []
        for sent1 in sentences1:
            row = []
            for sent2 in sentences2:
                # Calculate similarity between sentences
                sim = difflib.SequenceMatcher(None, sent1, sent2).ratio()
                row.append(sim)
            sentence_sim_matrix.append(row)
        
        # Find the best matches for each sentence in document 1
        top_sentence_matches = []
        for i, sent1 in enumerate(sentences1[:20]):  # Limit to first 20 sentences for performance
            best_matches = sorted([(j, sentence_sim_matrix[i][j]) for j in range(len(sentences2))], 
                                 key=lambda x: x[1], reverse=True)[:1]  # Get top match
            
            if best_matches and best_matches[0][1] > 0.4:  # Only include if similarity > 0.4
                top_sentence_matches.append((i, best_matches[0][0], best_matches[0][1]))
        
        # Display the best sentence matches
        for i, j, sim in top_sentence_matches:
            html_output.extend([
                '            <div class="sentence-pair">',
                f'                <div class="sentence-1">Document 1: {sentences1[i]}</div>',
                f'                <div class="match-score">{sim:.2f}</div>',
                f'                <div class="sentence-2">Document 2: {sentences2[j]}</div>',
                '            </div>'
            ])
        
        html_output.append('        </div>')
        html_output.append('    </div>')
        
        # Shared n-grams tab
        html_output.extend([
            '    <!-- Shared phrases tab -->',
            '    <div id="ngram-view" class="tab-content">',
            '        <h2>Shared Phrases (5-word sequences)</h2>',
            '        <p>The following phrases appear in both documents, indicating similar expressions:</p>',
            '        <table>',
            '            <tr><th>Phrase</th><th>Occurrences in Document 1</th><th>Occurrences in Document 2</th></tr>'
        ])
        
        # Add shared n-grams as a table
        for i, (ngram, occurrences) in enumerate(list(shared_ngrams.items())[:30]):
            doc1_occurrences = len([pos for pos, _ in occurrences])
            doc2_occurrences = sum(len(pos_list) for _, pos_list in occurrences)
            html_output.append(f'            <tr><td class="key-phrase">"{ngram}"</td><td>{doc1_occurrences}</td><td>{doc2_occurrences}</td></tr>')
        
        if len(shared_ngrams) > 30:
            html_output.append(f'            <tr><td colspan="3">... and {len(shared_ngrams) - 30} more phrases</td></tr>')
        
        html_output.append('        </table>')
        html_output.append('    </div>')
        
        # Heatmap tab
        html_output.extend([
            '    <!-- Heatmap tab -->',
            '    <div id="heatmap-view" class="tab-content">',
            '        <h2>Similarity Heatmap</h2>',
            '        <p>This heatmap visualizes the similarity between sentences in both documents:</p>',
            '        <div class="heatmap">',
            '            <img src="similarity_heatmap.png" alt="Similarity Heatmap">',
            '        </div>',
            '        <p>Brighter colors indicate higher similarity between sentences. This helps identify where ideas from one document appear in the other.</p>',
            '    </div>'
        ])
        
        # Calculate statistics for the statistics tab
        paragraph_similarities = para_similarities
        avg_paragraph_similarity = sum(paragraph_similarities) / max(len(paragraph_similarities), 1)
        
        # Stats tab
        html_output.extend([
            '    <!-- Statistics tab -->',
            '    <div id="stats-view" class="tab-content">',
            '        <h2>Document Statistics</h2>',
            '        <table>',
            '            <tr><th>Metric</th><th>Document 1</th><th>Document 2</th></tr>',
            f'            <tr><td>Word count</td><td>{len(text1.split())}</td><td>{len(text2.split())}</td></tr>',
            f'            <tr><td>Character count</td><td>{len(text1)}</td><td>{len(text2)}</td></tr>',
            f'            <tr><td>Paragraph count</td><td>{len(paragraphs1)}</td><td>{len(paragraphs2)}</td></tr>',
            f'            <tr><td>Sentence count</td><td>{len(sentences1)}</td><td>{len(sentences2)}</td></tr>',
            f'            <tr><td>Average sentence length (words)</td><td>{len(text1.split()) / max(1, len(sentences1)):.2f}</td><td>{len(text2.split()) / max(1, len(sentences2)):.2f}</td></tr>',
            f'            <tr><td>Common 5-word phrases</td><td colspan="2">{len(shared_ngrams)}</td></tr>',
            f'            <tr><td>Citation references</td><td>{len(re.findall(r"\\(parencite|textcite|cite)\{[^}]+\}", text1))}</td><td>{len(re.findall(r"\\(parencite|textcite|cite)\{[^}]+\}", text2))}</td></tr>',
            '        </table>',
            '        <h3>Similarity Analysis</h3>',
            '        <ul>',
            f'            <li>Overall document similarity: {similarity:.2f}</li>',
            f'            <li>Average paragraph-to-paragraph similarity: {avg_paragraph_similarity:.2f}</li>',
            f'            <li>Number of highly similar paragraphs (>0.7): {sum(1 for ratio in paragraph_similarities if ratio > 0.7)}</li>',
            f'            <li>Word overlap (Jaccard similarity): {len(set(text1.split()).intersection(set(text2.split()))) / len(set(text1.split()).union(set(text2.split()))):.2f}</li>',
            '        </ul>',
            '        <h3>Paraphrasing Analysis</h3>',
            '        <p>This section analyzes how content has been rephrased between documents:</p>',
            '        <ul>',
            f'            <li>Similar ideas, different wording: {sum(1 for ratio in paragraph_similarities if 0.4 <= ratio <= 0.7)} paragraphs</li>',
            f'            <li>Nearly identical content: {sum(1 for ratio in paragraph_similarities if ratio > 0.7)} paragrap