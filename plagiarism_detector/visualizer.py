"""
Visualization Tools for Plagiarism Detection

This module contains functions for creating visualizations of text similarity.
"""

import matplotlib.pyplot as plt
import numpy as np
import difflib
import seaborn as sns
from pathlib import Path
from typing import List, Optional

from plagiarism_detector.text_processor import get_sentences, preprocess_text
from plagiarism_detector.file_handler import ensure_output_dir, get_output_filename


def create_similarity_heatmap(text1: str, text2: str, output_file: Optional[str] = None, 
                             max_sentences: int = 20) -> str:
    """
    Create and save a heatmap showing sentence-level similarities.
    
    Args:
        text1: First text document
        text2: Second text document
        output_file: Optional path to save the heatmap image
        max_sentences: Maximum number of sentences to include in the visualization
        
    Returns:
        Path to the saved heatmap image
    """
    # Get sentences, limiting to a reasonable number for visualization
    sentences1 = get_sentences(preprocess_text(text1))[:max_sentences]
    sentences2 = get_sentences(preprocess_text(text2))[:max_sentences]
    
    # Create similarity matrix
    similarity_matrix = np.zeros((len(sentences1), len(sentences2)))
    
    # Compute similarity scores using difflib for sentence-level comparison
    for i, sent1 in enumerate(sentences1):
        for j, sent2 in enumerate(sentences2):
            if sent1 and sent2:
                similarity_matrix[i, j] = difflib.SequenceMatcher(None, sent1, sent2).ratio()
    
    # Create a heatmap
    plt.figure(figsize=(14, 10))
    
    ax = sns.heatmap(
        similarity_matrix, 
        annot=False,
        cmap="YlGnBu",
        xticklabels=[f"S{i+1}" for i in range(len(sentences2))], 
        yticklabels=[f"S{i+1}" for i in range(len(sentences1))],
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Similarity Score'}
    )
    
    # Improve visualization
    plt.title("Text Similarity Heatmap (Sentence Level)", fontsize=16)
    plt.xlabel("Document 2 Sentences", fontsize=12)
    plt.ylabel("Document 1 Sentences", fontsize=12)
    
    # Adjust to make text more legible
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    
    # Tight layout to maximize visualization space
    plt.tight_layout()
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("similarity_heatmap", "png")
    
    # Save the figure
    plt.savefig(output_file, bbox_inches='tight', dpi=150)
    plt.close()
    
    return output_file


def create_similarity_gauge(similarity: float, output_file: Optional[str] = None) -> str:
    """
    Create and save a gauge visualization showing the similarity level.
    
    Args:
        similarity: Similarity score (0.0 to 1.0)
        output_file: Optional path to save the gauge image
        
    Returns:
        Path to the saved gauge image
    """
    # Create gauge figure
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Define gauge settings
    gauge_height = 0.3
    gauge_width = 0.8
    
    # Define color gradient
    cmap = plt.cm.RdYlGn
    gauge_colors = cmap(np.linspace(0, 1, 256))
    
    # Draw background gauge (gray)
    ax.barh(0, gauge_width, height=gauge_height, left=0, color='lightgray')
    
    # Draw filled gauge with color based on value
    color_index = int(similarity * 255)
    if color_index > 255:
        color_index = 255
    if color_index < 0:
        color_index = 0
    ax.barh(0, similarity * gauge_width, height=gauge_height, left=0, color=gauge_colors[color_index])
    
    # Add score text
    ax.text(
        gauge_width / 2, 0, 
        f"{similarity:.2f}", 
        ha='center', va='center', 
        fontsize=14, fontweight='bold'
    )
    
    # Add low/high labels
    ax.text(0, -0.2, "Low", ha='left', va='top', fontsize=10)
    ax.text(gauge_width, -0.2, "High", ha='right', va='top', fontsize=10)
    
    # Remove axes and set limits
    ax.axis('off')
    ax.set_xlim(0, gauge_width)
    ax.set_ylim(-0.5, 0.5)
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("similarity_gauge", "png")
    
    # Save the figure
    plt.savefig(output_file, bbox_inches='tight', dpi=150, transparent=True)
    plt.close()
    
    return output_file


def create_bar_chart_comparison(metrics: dict, output_file: Optional[str] = None) -> str:
    """
    Create a bar chart comparing different similarity metrics.
    
    Args:
        metrics: Dictionary of similarity metrics
        output_file: Optional path to save the chart image
        
    Returns:
        Path to the saved chart image
    """
    # Prepare data
    labels = list(metrics.keys())
    values = list(metrics.values())
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create bars with gradient colors
    bars = plt.bar(labels, values, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(labels))))
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{height:.2f}',
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    # Add labels and title
    plt.ylabel('Similarity Score')
    plt.title('Comparison of Similarity Metrics')
    plt.ylim(0, 1.1)  # Set y-axis limit with some padding
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=30, ha='right')
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Tight layout
    plt.tight_layout()
    
    # Generate output filename if not provided
    if not output_file:
        output_file = get_output_filename("metrics_comparison", "png")
    
    # Save the figure
    plt.savefig(output_file, bbox_inches='tight', dpi=150)
    plt.close()
    
    return output_file