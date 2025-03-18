"""
Text Processing Utilities for Plagiarism Detection

This module contains functions for preprocessing and analyzing text documents.
"""

import re
from typing import List, Set
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


def ensure_nltk_resources() -> None:
    """
    Ensure that required NLTK resources are downloaded.
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)


def preprocess_text(text: str) -> str:
    """
    Clean and preprocess text, preserving paragraph structure.
    Handles LaTeX citations and commands properly.
    
    Args:
        text: Raw text to process
        
    Returns:
        Preprocessed text
    """
    # Replace LaTeX citations with placeholders
    text = re.sub(r'\\parencite\{[^}]+\}', '[CITATION]', text)
    text = re.sub(r'\\textcite\{[^}]+\}', '[CITATION]', text)
    text = re.sub(r'\\cite\{[^}]+\}', '[CITATION]', text)
    
    # Handle LaTeX quotes
    text = re.sub(r"''", '"', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '[EMAIL]', text)
    
    # Normalize whitespace but preserve paragraph breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    # Remove section headers (e.g., "Journal paper:", "Masters thesis:")
    text = re.sub(r'^[^:]+:\s*', '', text)
    
    return text


def get_sentences(text: str) -> List[str]:
    """
    Split text into sentences using NLTK's sentence tokenizer.
    
    Args:
        text: Text to split into sentences
        
    Returns:
        List of sentences
    """
    # First handle LaTeX period notations that shouldn't be split
    text = re.sub(r'\.\s*\\', '.\\', text)
    
    # Use NLTK's sentence tokenizer
    sentences = sent_tokenize(text)
    
    # Clean up the sentences and remove empty ones
    return [s.strip() for s in sentences if s.strip()]


def tokenize_and_filter(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Tokenize text and optionally remove stopwords.
    
    Args:
        text: Text to tokenize
        remove_stopwords: Whether to remove common stopwords
        
    Returns:
        List of tokens
    """
    words = word_tokenize(text.lower())
    
    if remove_stopwords:
        stop_words = set(stopwords.words('english'))
        return [word for word in words if word.isalnum() and word not in stop_words]
    else:
        return [word for word in words if word.isalnum()]


def get_ngrams(text: str, n: int = 3, tokenized: bool = False) -> Set[str]:
    """
    Generate n-grams from text.
    
    Args:
        text: Text to generate n-grams from
        n: Size of n-gram (number of words)
        tokenized: Whether the text is already tokenized
        
    Returns:
        Set of n-grams
    """
    tokens = text if tokenized else tokenize_and_filter(text)
    return set(' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1))