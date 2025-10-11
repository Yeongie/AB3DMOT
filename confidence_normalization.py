#!/usr/bin/env python3
"""
Confidence Score Normalization for PointRCNN Detections
========================================================

This script provides multiple methods to normalize PointRCNN confidence scores
from their raw logit values to 0.0-1.0 probability range.

Author: AB3DMOT Team
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union, Tuple, List
import os


class ConfidenceNormalizer:
    """
    Class to normalize PointRCNN confidence scores using various methods.
    """
    
    def __init__(self):
        self.method_stats = {}
    
    def sigmoid_normalization(self, raw_scores: np.ndarray) -> np.ndarray:
        """
        Method 1: Sigmoid transformation (most common for logits)
        
        Formula: sigmoid(x) = 1 / (1 + exp(-x))
        
        Args:
            raw_scores: Raw PointRCNN confidence scores (logits)
            
        Returns:
            Normalized scores in [0, 1] range
        """
        # Clip extreme values to prevent overflow
        clipped_scores = np.clip(raw_scores, -50, 50)
        normalized = 1 / (1 + np.exp(-clipped_scores))
        
        self.method_stats['sigmoid'] = {
            'input_range': (raw_scores.min(), raw_scores.max()),
            'output_range': (normalized.min(), normalized.max()),
            'method': 'sigmoid'
        }
        
        return normalized
    
    def min_max_normalization(self, raw_scores: np.ndarray, 
                            custom_range: Tuple[float, float] = None) -> np.ndarray:
        """
        Method 2: Min-Max scaling to [0, 1]
        
        Formula: (x - min) / (max - min)
        
        Args:
            raw_scores: Raw confidence scores
            custom_range: Optional (min, max) to use instead of data range
            
        Returns:
            Normalized scores in [0, 1] range
        """
        if custom_range:
            min_val, max_val = custom_range
        else:
            min_val, max_val = raw_scores.min(), raw_scores.max()
        
        # Avoid division by zero
        if max_val == min_val:
            normalized = np.ones_like(raw_scores) * 0.5
        else:
            normalized = (raw_scores - min_val) / (max_val - min_val)
        
        # Ensure values are in [0, 1]
        normalized = np.clip(normalized, 0, 1)
        
        self.method_stats['min_max'] = {
            'input_range': (min_val, max_val),
            'output_range': (normalized.min(), normalized.max()),
            'method': 'min_max'
        }
        
        return normalized
    
    def z_score_sigmoid_normalization(self, raw_scores: np.ndarray) -> np.ndarray:
        """
        Method 3: Z-score normalization followed by sigmoid
        
        Steps:
        1. Standardize: (x - mean) / std
        2. Apply sigmoid: 1 / (1 + exp(-z))
        
        Args:
            raw_scores: Raw confidence scores
            
        Returns:
            Normalized scores in [0, 1] range
        """
        # Z-score normalization
        mean_score = raw_scores.mean()
        std_score = raw_scores.std()
        
        if std_score == 0:
            z_scores = np.zeros_like(raw_scores)
        else:
            z_scores = (raw_scores - mean_score) / std_score
        
        # Apply sigmoid to z-scores
        normalized = 1 / (1 + np.exp(-z_scores))
        
        self.method_stats['z_score_sigmoid'] = {
            'input_range': (raw_scores.min(), raw_scores.max()),
            'output_range': (normalized.min(), normalized.max()),
            'mean': mean_score,
            'std': std_score,
            'method': 'z_score_sigmoid'
        }
        
        return normalized
    
    def percentile_normalization(self, raw_scores: np.ndarray, 
                                percentiles: Tuple[float, float] = (5, 95)) -> np.ndarray:
        """
        Method 4: Percentile-based normalization (robust to outliers)
        
        Uses percentiles instead of min/max to handle outliers
        
        Args:
            raw_scores: Raw confidence scores
            percentiles: (low_percentile, high_percentile) to use as range
            
        Returns:
            Normalized scores in [0, 1] range
        """
        low_perc, high_perc = percentiles
        min_val = np.percentile(raw_scores, low_perc)
        max_val = np.percentile(raw_scores, high_perc)
        
        if max_val == min_val:
            normalized = np.ones_like(raw_scores) * 0.5
        else:
            normalized = (raw_scores - min_val) / (max_val - min_val)
        
        # Clip to [0, 1] range
        normalized = np.clip(normalized, 0, 1)
        
        self.method_stats['percentile'] = {
            'input_range': (raw_scores.min(), raw_scores.max()),
            'percentile_range': (min_val, max_val),
            'output_range': (normalized.min(), normalized.max()),
            'percentiles_used': percentiles,
            'method': 'percentile'
        }
        
        return normalized


def analyze_confidence_scores(csv_file_path: str) -> pd.DataFrame:
    """
    Analyze confidence scores from a CSV file
    
    Args:
        csv_file_path: Path to CSV file with tracking results
        
    Returns:
        DataFrame with confidence score statistics
    """
    df = pd.read_csv(csv_file_path)
    
    if 'confidence_score' not in df.columns:
        raise ValueError("CSV file must contain 'confidence_score' column")
    
    conf_scores = df['confidence_score'].values
    
    stats = {
        'count': len(conf_scores),
        'mean': conf_scores.mean(),
        'std': conf_scores.std(),
        'min': conf_scores.min(),
        'max': conf_scores.max(),
        'median': np.median(conf_scores),
        'q25': np.percentile(conf_scores, 25),
        'q75': np.percentile(conf_scores, 75),
        'negative_count': np.sum(conf_scores < 0),
        'positive_count': np.sum(conf_scores > 0),
        'zero_count': np.sum(conf_scores == 0)
    }
    
    return pd.DataFrame([stats])


def normalize_csv_confidence_scores(input_csv: str, output_csv: str, 
                                  method: str = 'sigmoid') -> None:
    """
    Normalize confidence scores in a CSV file and save to new file
    
    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
        method: Normalization method ('sigmoid', 'min_max', 'z_score_sigmoid', 'percentile')
    """
    # Read CSV
    df = pd.read_csv(input_csv)
    
    if 'confidence_score' not in df.columns:
        raise ValueError("CSV file must contain 'confidence_score' column")
    
    # Extract confidence scores
    raw_scores = df['confidence_score'].values
    
    # Initialize normalizer
    normalizer = ConfidenceNormalizer()
    
    # Apply normalization
    if method == 'sigmoid':
        normalized_scores = normalizer.sigmoid_normalization(raw_scores)
    elif method == 'min_max':
        normalized_scores = normalizer.min_max_normalization(raw_scores)
    elif method == 'z_score_sigmoid':
        normalized_scores = normalizer.z_score_sigmoid_normalization(raw_scores)
    elif method == 'percentile':
        normalized_scores = normalizer.percentile_normalization(raw_scores)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Update DataFrame
    df['confidence_score_raw'] = raw_scores
    df['confidence_score'] = normalized_scores
    
    # Save to new CSV
    df.to_csv(output_csv, index=False)
    
    print(f"✅ Normalized confidence scores using {method} method")
    print(f"📊 Input range: [{raw_scores.min():.3f}, {raw_scores.max():.3f}]")
    print(f"📊 Output range: [{normalized_scores.min():.3f}, {normalized_scores.max():.3f}]")
    print(f"💾 Saved to: {output_csv}")


def compare_normalization_methods(raw_scores: np.ndarray, 
                                save_plot: str = None) -> None:
    """
    Compare different normalization methods visually
    
    Args:
        raw_scores: Raw confidence scores
        save_plot: Optional path to save comparison plot
    """
    normalizer = ConfidenceNormalizer()
    
    # Apply all methods
    methods = {
        'Original': raw_scores,
        'Sigmoid': normalizer.sigmoid_normalization(raw_scores),
        'Min-Max': normalizer.min_max_normalization(raw_scores),
        'Z-Score + Sigmoid': normalizer.z_score_sigmoid_normalization(raw_scores),
        'Percentile': normalizer.percentile_normalization(raw_scores)
    }
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (method_name, scores) in enumerate(methods.items()):
        ax = axes[i]
        ax.hist(scores, bins=50, alpha=0.7, edgecolor='black')
        ax.set_title(f'{method_name}\nRange: [{scores.min():.3f}, {scores.max():.3f}]')
        ax.set_xlabel('Confidence Score')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
    
    # Hide the last empty subplot
    axes[-1].set_visible(False)
    
    plt.tight_layout()
    plt.suptitle('Comparison of Confidence Score Normalization Methods', 
                 fontsize=16, y=1.02)
    
    if save_plot:
        plt.savefig(save_plot, dpi=300, bbox_inches='tight')
        print(f"📈 Comparison plot saved to: {save_plot}")
    
    plt.show()


# Example usage and testing
if __name__ == "__main__":
    # Example with sample data similar to your PointRCNN scores
    sample_scores = np.array([
        2.3895, 1.9132, -0.7391, -1.7867, 0.4509, 2.2863, 
        -1.1316, 1.2704, -0.1005, 0.8723, -2.1541, 1.6644
    ])
    
    print("🔧 Confidence Score Normalization Demo")
    print("=" * 50)
    
    normalizer = ConfidenceNormalizer()
    
    print(f"📊 Original scores: {sample_scores}")
    print(f"📊 Range: [{sample_scores.min():.3f}, {sample_scores.max():.3f}]")
    print()
    
    # Test all methods
    methods_to_test = [
        ('sigmoid', 'Sigmoid (recommended for logits)'),
        ('min_max', 'Min-Max scaling'),
        ('z_score_sigmoid', 'Z-score + Sigmoid'),
        ('percentile', 'Percentile-based (robust)')
    ]
    
    results = {}
    for method_key, method_desc in methods_to_test:
        print(f"🎯 {method_desc}:")
        
        if method_key == 'sigmoid':
            normalized = normalizer.sigmoid_normalization(sample_scores)
        elif method_key == 'min_max':
            normalized = normalizer.min_max_normalization(sample_scores)
        elif method_key == 'z_score_sigmoid':
            normalized = normalizer.z_score_sigmoid_normalization(sample_scores)
        elif method_key == 'percentile':
            normalized = normalizer.percentile_normalization(sample_scores)
        
        results[method_key] = normalized
        print(f"   Normalized: {normalized}")
        print(f"   Range: [{normalized.min():.3f}, {normalized.max():.3f}]")
        print()
    
    # Show comparison
    print("📈 Creating comparison visualization...")
    compare_normalization_methods(sample_scores, 'confidence_normalization_comparison.png')
