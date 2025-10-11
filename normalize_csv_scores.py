#!/usr/bin/env python3
"""
Simple script to normalize confidence scores in AB3DMOT CSV files
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path


def sigmoid_normalize(raw_scores):
    """Apply sigmoid normalization to convert logits to probabilities"""
    # Clip extreme values to prevent overflow
    clipped = np.clip(raw_scores, -50, 50)
    return 1 / (1 + np.exp(-clipped))


def normalize_csv_file(input_path, output_path=None):
    """
    Normalize confidence scores in a single CSV file
    
    Args:
        input_path: Path to input CSV file
        output_path: Path for output file (if None, adds '_normalized' suffix)
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Error reading {input_path}: {e}")
        return False
    
    # Check if confidence_score column exists
    if 'confidence_score' not in df.columns:
        print(f"❌ No 'confidence_score' column found in {input_path}")
        return False
    
    # Get raw scores
    raw_scores = df['confidence_score'].values
    
    # Apply sigmoid normalization (recommended for PointRCNN logits)
    normalized_scores = sigmoid_normalize(raw_scores)
    
    # Create output DataFrame
    df_output = df.copy()
    df_output['confidence_score_raw'] = raw_scores  # Keep original scores
    df_output['confidence_score'] = normalized_scores  # Replace with normalized
    
    # Determine output path
    if output_path is None:
        input_file = Path(input_path)
        output_path = input_file.parent / f"{input_file.stem}_normalized{input_file.suffix}"
    
    # Save normalized CSV
    try:
        df_output.to_csv(output_path, index=False)
        
        print(f"✅ Normalized {input_path}")
        print(f"   📊 Original range: [{raw_scores.min():.3f}, {raw_scores.max():.3f}]")
        print(f"   📊 Normalized range: [{normalized_scores.min():.3f}, {normalized_scores.max():.3f}]")
        print(f"   💾 Saved to: {output_path}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving {output_path}: {e}")
        return False


if __name__ == "__main__":
    print("🔧 AB3DMOT Confidence Score Normalizer")
    print("=" * 50)
    
    # Check if we're in a directory with example CSV files
    example_files = glob.glob("example_output/*.csv")
    
    if example_files:
        print(f"📁 Found example CSV files:")
        for f in example_files:
            print(f"   - {f}")
        
        print("\n🔄 Normalizing example files...")
        for csv_file in example_files:
            normalize_csv_file(csv_file)
    else:
        print("❌ No CSV files found in example_output/.")
        print("💡 Usage: normalize_csv_file('your_file.csv')")
        
        # Show sample transformation
        print("\n📊 Sample PointRCNN confidence score transformation:")
        sample_scores = np.array([2.39, 1.91, -0.74, -1.79, 0.45])
        normalized = sigmoid_normalize(sample_scores)
        
        print("Original → Normalized")
        for orig, norm in zip(sample_scores, normalized):
            print(f"{orig:6.2f} → {norm:.3f}")