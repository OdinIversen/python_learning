"""
Report Generators for Plagiarism Detection

This module contains functions for generating various types of reports.
"""

import difflib
import re
import html
import json
import uuid
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from plagiarism_detector.text_processor import preprocess_text, get_sentences
from plagiarism_detector.visualizer import create_similarity_heatmap
from plagiarism_detector.file_handler import save_text_file, save_json_file, get_output_filename


def generate_text_diff(text1: str, text2: str, output_file: Optional[str] = None) -> str:
    """
    Generate a plain text diff between two documents.
    
    Args:
        text1: First text document
        text2: Second text document
        output_file: Optional path to save the diff
        
    Returns:
        Path to the saved diff file
    """
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Split into lines for comparison
    lines1 = processed_text1.split('\n')
    lines2 = processed_text2.split('\n')
    
    # Generate diff
    diff = difflib.unified_diff(lines1, lines2, lineterm='', n=3)
    diff_text = '\n'.join(diff)
    
    if not output_file:
        # Generate default output filename
        output_file = get_output_filename("text_diff", "txt")
    
    return save_text_file(diff_text, output_file)


def generate_json_report(text1: str, text2: str, similarity_metrics: Dict[str, float], 
                       shared_ngrams: Dict, output_file: Optional[str] = None,
                       title1: str = "Document 1", title2: str = "Document 2") -> str:
    """
    Generate a JSON report with all similarity metrics and analysis.
    
    Args:
        text1: First text document
        text2: Second text document
        similarity_metrics: Dictionary of similarity metrics
        shared_ngrams: Dictionary of shared n-grams
        output_file: Optional path to save the JSON output
        title1: Title for the first document
        title2: Title for the second document
        
    Returns:
        Path to the generated JSON report
    """
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Get sentences
    sentences1 = get_sentences(processed_text1)
    sentences2 = get_sentences(processed_text2)
    
    # Extract top shared phrases
    top_shared_phrases = []
    
    for ngram, occurrences in list(shared_ngrams.items())[:20]:
        doc1_occurrences = len([pos for pos, _ in occurrences])
        doc2_occurrences = sum(len(pos_list) for _, pos_list in occurrences)
        top_shared_phrases.append({
            "phrase": ngram,
            "doc1_count": doc1_occurrences,
            "doc2_count": doc2_occurrences
        })
    
    # Create the report dictionary
    report = {
        "report_date": datetime.now().isoformat(),
        "document1": {
            "title": title1,
            "word_count": len(text1.split()),
            "character_count": len(text1),
            "sentence_count": len(sentences1)
        },
        "document2": {
            "title": title2,
            "word_count": len(text2.split()),
            "character_count": len(text2),
            "sentence_count": len(sentences2)
        },
        "similarity_metrics": similarity_metrics,
        "shared_phrases": top_shared_phrases,
        "interpretation": {
            "similarity_level": "high" if similarity_metrics["combined_similarity"] >= 0.8 else
                                "moderate" if similarity_metrics["combined_similarity"] >= 0.5 else
                                "low"
        }
    }
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("similarity_report", "json")
    
    # Save JSON to file
    return save_json_file(report, output_file)


def generate_html_report(text1: str, text2: str, similarity_metrics: Dict[str, float], 
                      shared_ngrams: Dict, output_file: Optional[str] = None,
                      title1: str = "Document 1", title2: str = "Document 2") -> str:
    """
    Generate a comprehensive HTML report showing similarities and differences between texts.
    
    Args:
        text1: First text document
        text2: Second text document
        similarity_metrics: Dictionary of similarity metrics
        shared_ngrams: Dictionary of shared n-grams
        output_file: Path to save the HTML output
        title1: Title for the first document
        title2: Title for the second document
        
    Returns:
        Path to the generated HTML report
    """
    # Get overall similarity
    similarity = similarity_metrics["combined_similarity"]
    
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Split the texts into paragraphs for better readability
    paragraphs1 = [p.strip() for p in processed_text1.split('\n\n') if p.strip()]
    paragraphs2 = [p.strip() for p in processed_text2.split('\n\n') if p.strip()]
    
    # Get sentences for sentence-level comparison
    sentences1 = get_sentences(processed_text1)
    sentences2 = get_sentences(processed_text2)
    
    # Generate heatmap for visualization
    heatmap_result_dir = os.path.join("personal_files", "plagiarism_results")
    heatmap_file = os.path.join(heatmap_result_dir, f"heatmap_{uuid.uuid4().hex[:8]}.png")
    heatmap_path = create_similarity_heatmap(processed_text1, processed_text2, heatmap_file)
    heatmap_relative_path = os.path.basename(heatmap_path)
    
    # Create HTML with proper formatting (header)
    html_output = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>Text Similarity Analysis: {title1} vs {title2}</title>',
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
        '        .sentence-comparison { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 15px; }',
        '        .sentence-pair { display: flex; border-bottom: 1px dashed #ccc; padding-bottom: 10px; margin-bottom: 10px; }',
        '        .sentence-1, .sentence-2 { flex: 1; padding: 5px; }',
        '        .match-score { font-size: 0.9em; text-align: center; background: #eee; padding: 2px 5px; border-radius: 3px; margin: 0 5px; }',
        '        .key-phrase { background-color: #e6f3ff; padding: 2px 4px; border-radius: 3px; }',
        '        .meter { height: 20px; position: relative; background: #f3f3f3; border-radius: 25px; padding: 5px; box-shadow: inset 0 -1px 1px rgba(255, 255, 255, 0.3); }',
        '        .meter > span { display: block; height: 100%; border-radius: 8px; position: relative; overflow: hidden; }',
        '        .high { background-color: rgb(43, 194, 83); }',
        '        .medium { background-color: rgb(255, 187, 0); }',
        '        .low { background-color: rgb(224, 98, 98); }',
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
        f'    <h1>Text Similarity Analysis: {title1} vs {title2}</h1>',
        '    <div class="stats">',
        '        <h2>Similarity Summary</h2>',
        '        <div class="meter">',
    ]
    
    # Add similarity gauge
    gauge_class = "high" if similarity >= 0.8 else "medium" if similarity >= 0.5 else "low"
    html_output.append(f'            <span style="width: {similarity * 100}%" class="{gauge_class}"></span>')
    html_output.append('        </div>')
    
    # Add interpretation
    html_output.extend([
        f'        <p><span class="similarity-score">Overall Similarity Score: {similarity:.2f}</span></p>',
        '        <div class="summary">',
    ])
    
    if similarity >= 0.8:
        html_output.append('            <p class="similar"><strong>HIGH SIMILARITY</strong> - Significant overlap in content and wording</p>')
    elif similarity >= 0.5:
        html_output.append('            <p class="moderate"><strong>MODERATE SIMILARITY</strong> - Similar ideas with different expressions</p>')
    else:
        html_output.append('            <p class="different"><strong>LOW SIMILARITY</strong> - Substantially different texts</p>')
    
    html_output.append('        </div>')
    
    # Add detailed metrics
    html_output.extend([
        '        <h3>Detailed Similarity Metrics</h3>',
        '        <table>',
        '            <tr><th>Metric</th><th>Score</th><th>Description</th></tr>',
        f'            <tr><td>Cosine Similarity</td><td>{similarity_metrics.get("cosine_similarity", 0):.2f}</td><td>Measures how similar the document vectors are</td></tr>',
        f'            <tr><td>Jaccard Similarity</td><td>{similarity_metrics.get("jaccard_similarity", 0):.2f}</td><td>Measures word overlap between documents</td></tr>',
        f'            <tr><td>Sequence Similarity</td><td>{similarity_metrics.get("sequence_similarity", 0):.2f}</td><td>Measures character-by-character similarity</td></tr>',
        f'            <tr><td>N-gram Similarity</td><td>{similarity_metrics.get("ngram_similarity", 0):.2f}</td><td>Measures phrase overlap</td></tr>',
        '        </table>',
        '    </div>',
    ])
    
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
        html_output.append(f'            <div class="doc"><h3>{title1} - Paragraph {i+1}</h3>')
        
        # Find the best matching paragraph in document 2
        best_match_idx = -1
        best_ratio = 0
        
        for j, paragraph2 in enumerate(paragraphs2):
            ratio = difflib.SequenceMatcher(None, paragraph1, paragraph2).ratio()
            if ratio > best_ratio and ratio > 0.3:
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
                    paragraph1_html.append(f'<span class="highlight">{html.escape(paragraph1[i1:i2])}</span>')
                else:
                    paragraph1_html.append(html.escape(paragraph1[i1:i2]))
            
            html_output.append(f'            <div class="paragraph">{"".join(paragraph1_html)}</div>')
            html_output.append(f'            <p class="similar">Similarity to {title2}, Paragraph {best_match_idx+1}: {best_ratio:.2f}</p>')
        else:
            html_output.append(f'            <div class="paragraph">{html.escape(paragraph1)}</div>')
            html_output.append(f'            <p class="different">No similar paragraph found in {title2}</p>')
        
        html_output.append('            </div>')
        
        # Show the matching paragraph from document 2 if one was found
        if best_match_idx >= 0:
            html_output.append(f'            <div class="doc"><h3>{title2} - Paragraph {best_match_idx+1}</h3>')
            
            # Format paragraph 2
            s = difflib.SequenceMatcher(None, paragraph1, paragraphs2[best_match_idx])
            paragraph2_html = []
            
            for tag, i1, i2, j1, j2 in s.get_opcodes():
                if tag == 'equal' and i2-i1 > 5:  # Only highlight substantial matches
                    paragraph2_html.append(f'<span class="highlight">{html.escape(paragraphs2[best_match_idx][j1:j2])}</span>')
                else:
                    paragraph2_html.append(html.escape(paragraphs2[best_match_idx][j1:j2]))
            
            html_output.append(f'            <div class="paragraph">{"".join(paragraph2_html)}</div>')
            html_output.append('            </div>')
        else:
            html_output.append(f'            <div class="doc"><h3>{title2}</h3>')
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
            f'                <div class="sentence-1">{title1}: {html.escape(sentences1[i])}</div>',
            f'                <div class="match-score">{sim:.2f}</div>',
            f'                <div class="sentence-2">{title2}: {html.escape(sentences2[j])}</div>',
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
        html_output.append(f'            <tr><td class="key-phrase">"{html.escape(ngram)}"</td><td>{doc1_occurrences}</td><td>{doc2_occurrences}</td></tr>')
    
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
        f'            <img src="{heatmap_relative_path}" alt="Similarity Heatmap">',
        '        </div>',
        '        <p>Brighter colors indicate higher similarity between sentences. This helps identify where ideas from one document appear in the other.</p>',
        '    </div>'
    ])
    
    # Statistics tab
    html_output.extend([
        '    <!-- Statistics tab -->',
        '    <div id="stats-view" class="tab-content">',
        '        <h2>Document Statistics</h2>',
        '        <table>',
        '            <tr><th>Metric</th><th>' + title1 + '</th><th>' + title2 + '</th></tr>',
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
        f'            <li>Average paragraph-to-paragraph similarity: {sum(para_similarities) / max(len(para_similarities), 1):.2f}</li>',
        f'            <li>Number of highly similar paragraphs (>0.7): {sum(1 for ratio in para_similarities if ratio > 0.7)}</li>',
        f'            <li>Word overlap (Jaccard similarity): {similarity_metrics.get("jaccard_similarity", 0):.2f}</li>',
        '        </ul>',
        '    </div>',
        
        '    <!-- Footer -->',
        '    <footer style="margin-top: 40px; text-align: center; color: #777; font-size: 0.9em; border-top: 1px solid #ddd; padding-top: 20px;">',
        f'        <p>Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
        '        <p>Python Learning Project - Plagiarism Detector</p>',
        '    </footer>',
        '</body>',
        '</html>'
    ])
    
    # Convert list to string
    html_content = '\n'.join(html_output)
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("similarity_report", "html")
    
    # Write HTML to file
    return save_text_file(html_content, output_file)


def generate_summary_report(text1: str, text2: str, similarity_metrics: Dict[str, float], 
                          shared_ngrams: Dict, output_file: Optional[str] = None,
                          title1: str = "Document 1", title2: str = "Document 2") -> str:
    """
    Generate a plain text summary report of the similarity analysis.
    
    Args:
        text1: First text document
        text2: Second text document
        similarity_metrics: Dictionary of similarity metrics
        shared_ngrams: Dictionary of shared n-grams
        output_file: Optional path to save the text output
        title1: Title for the first document
        title2: Title for the second document
        
    Returns:
        Path to the generated text report
    """
    # Get overall similarity
    similarity = similarity_metrics["combined_similarity"]
    
    # Determine similarity level
    if similarity >= 0.8:
        similarity_level = "HIGH"
        interpretation = "Significant overlap in content and wording"
    elif similarity >= 0.5:
        similarity_level = "MODERATE"
        interpretation = "Similar ideas with different expressions"
    else:
        similarity_level = "LOW"
        interpretation = "Substantially different texts"
    
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    # Get sentences for counts
    sentences1 = get_sentences(processed_text1)
    sentences2 = get_sentences(processed_text2)
    
    # Extract top shared phrases (limit to 5 for summary)
    top_shared_phrases = []
    for ngram, occurrences in list(shared_ngrams.items())[:5]:
        doc1_occurrences = len([pos for pos, _ in occurrences])
        doc2_occurrences = sum(len(pos_list) for _, pos_list in occurrences)
        top_shared_phrases.append(f'"{ngram}" (Found {doc1_occurrences} times in doc1, {doc2_occurrences} times in doc2)')
    
    # Create the summary text
    summary_lines = [
        "PLAGIARISM DETECTION SUMMARY REPORT",
        "=" * 50,
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Document 1: {title1}",
        f"Document 2: {title2}",
        "=" * 50,
        "",
        "SIMILARITY ANALYSIS",
        "-" * 20,
        f"Overall Similarity: {similarity:.2f}",
        f"Similarity Level: {similarity_level}",
        f"Interpretation: {interpretation}",
        "",
        "DETAILED METRICS",
        "-" * 20,
    ]
    
    # Add detailed metrics
    for metric, value in similarity_metrics.items():
        summary_lines.append(f"{metric.replace('_', ' ').title()}: {value:.2f}")
    
    # Add document statistics
    summary_lines.extend([
        "",
        "DOCUMENT STATISTICS",
        "-" * 20,
        f"{'Metric':<25} {'Document 1':<15} {'Document 2':<15}",
        f"{'Word count':<25} {len(text1.split()):<15} {len(text2.split()):<15}",
        f"{'Character count':<25} {len(text1):<15} {len(text2):<15}",
        f"{'Sentence count':<25} {len(sentences1):<15} {len(sentences2):<15}",
        "",
        "TOP SHARED PHRASES",
        "-" * 20,
    ])
    
    # Add top shared phrases
    for phrase in top_shared_phrases:
        summary_lines.append(f"- {phrase}")
    
    if not top_shared_phrases:
        summary_lines.append("No significant shared phrases found")
    
    # Add conclusion
    summary_lines.extend([
        "",
        "CONCLUSION",
        "-" * 20,
    ])
    
    if similarity >= 0.8:
        summary_lines.append("The documents show HIGH similarity and may contain significant plagiarism. Further investigation is recommended.")
    elif similarity >= 0.5:
        summary_lines.append("The documents show MODERATE similarity. Some sections may contain similar ideas expressed differently.")
    else:
        summary_lines.append("The documents show LOW similarity. Significant plagiarism is unlikely, though isolated instances may exist.")
    
    # Convert the lines to text
    summary_text = "\n".join(summary_lines)
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("similarity_summary", "txt")
    
    # Write text to file
    return save_text_file(summary_text, output_file)