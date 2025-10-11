#!/usr/bin/env python3
"""
Normalize confidence scores in AB3DMOT tracking result CSV files
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path


def sigmoid_normalize(raw_scores):
    """Apply sigmoid normalization to convert PointRCNN logits to probabilities"""
    # Clip extreme values to prevent overflow
    clipped = np.clip(raw_scores, -50, 50)
    return 1 / (1 + np.exp(-clipped))


def analyze_confidence_scores(csv_file):
    """Analyze the confidence scores in a CSV file"""
    try:
        df = pd.read_csv(csv_file)
        if 'confidence_score' not in df.columns:
            return None
        
        scores = df['confidence_score'].values
        return {
            'file': csv_file,
            'count': len(scores),
            'min': scores.min(),
            'max': scores.max(),
            'mean': scores.mean(),
            'std': scores.std(),
            'negative_count': np.sum(scores < 0),
            'positive_count': np.sum(scores > 0)
        }
    except Exception as e:
        print(f"❌ Error analyzing {csv_file}: {e}")
        return None


def normalize_csv_file(input_path, output_path=None, create_backup=True):
    """
    Normalize confidence scores in a single CSV file
    """
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Error reading {input_path}: {e}")
        return False
    
    if 'confidence_score' not in df.columns:
        print(f"❌ No 'confidence_score' column found in {input_path}")
        return False
    
    # Get raw scores
    raw_scores = df['confidence_score'].values
    
    # Apply sigmoid normalization
    normalized_scores = sigmoid_normalize(raw_scores)
    
    # Create backup if requested
    if create_backup:
        backup_path = str(input_path).replace('.csv', '_original.csv')
        df.to_csv(backup_path, index=False)
        print(f"📁 Created backup: {backup_path}")
    
    # Update the original DataFrame
    df['confidence_score_raw'] = raw_scores
    df['confidence_score'] = normalized_scores
    
    # Determine output path
    if output_path is None:
        output_path = input_path  # Overwrite original
    
    # Save normalized CSV
    try:
        df.to_csv(output_path, index=False)
        
        print(f"✅ Normalized {os.path.basename(input_path)}")
        print(f"   📊 Original range: [{raw_scores.min():.3f}, {raw_scores.max():.3f}]")
        print(f"   📊 Normalized range: [{normalized_scores.min():.3f}, {normalized_scores.max():.3f}]")
        print(f"   📈 Records: {len(raw_scores)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving {output_path}: {e}")
        return False


def process_all_tracking_results():
    """Process all tracking result CSV files in the current directory structure"""
    
    print("🔧 AB3DMOT Tracking Results Confidence Score Normalizer")
    print("=" * 60)
    
    # Find all CSV files
    csv_files = []
    for pattern in ['**/*tracking_results_*.csv', '**/tracking_results_*.csv']:
        csv_files.extend(glob.glob(pattern, recursive=True))
    
    if not csv_files:
        print("❌ No tracking result CSV files found!")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files to process")
    
    # First, analyze all files to understand the score distributions
    print("\n📊 Analyzing confidence score distributions...")
    all_stats = []
    
    for csv_file in csv_files[:5]:  # Analyze first 5 files for overview
        stats = analyze_confidence_scores(csv_file)
        if stats:
            all_stats.append(stats)
            print(f"   {os.path.basename(stats['file'])}: "
                  f"range=[{stats['min']:.2f}, {stats['max']:.2f}], "
                  f"mean={stats['mean']:.2f}, "
                  f"records={stats['count']}")
    
    if not all_stats:
        print("❌ No valid CSV files with confidence_score column found!")
        return
    
    # Ask user for confirmation
    print(f"\n🤔 Ready to normalize {len(csv_files)} files using sigmoid transformation:")
    print("   • Raw PointRCNN logits → 0.0-1.0 probabilities")
    print("   • Original files will be backed up as *_original.csv")
    print("   • Normalized scores will replace confidence_score column")
    print("   • Raw scores will be saved as confidence_score_raw column")
    
    response = input("\n❓ Proceed with normalization? (y/n): ").strip().lower()
    
    if response != 'y' and response != 'yes':
        print("❌ Normalization cancelled.")
        return
    
    # Process all files
    print(f"\n🔄 Processing {len(csv_files)} files...")
    success_count = 0
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\n[{i}/{len(csv_files)}] Processing {os.path.basename(csv_file)}...")
        
        if normalize_csv_file(csv_file, create_backup=(i <= 3)):  # Only backup first 3 files
            success_count += 1
    
    print(f"\n🎉 Successfully normalized {success_count}/{len(csv_files)} files!")
    print("\n📋 Summary:")
    print(f"   ✅ Normalized: {success_count} files")
    print(f"   ❌ Failed: {len(csv_files) - success_count} files")
    print(f"   📁 Backups created for first 3 files (*_original.csv)")
    print(f"   📊 Confidence scores now in 0.0-1.0 range")


def show_sample_transformation():
    """Show what the normalization looks like with sample data"""
    print("📊 Sample PointRCNN confidence score transformation:")
    print("-" * 50)
    
    # Use actual ranges from your data
    sample_scores = np.array([2.39, 1.91, 0.45, -0.74, -1.79, -2.15])
    normalized = sigmoid_normalize(sample_scores)
    
    print("   Raw Score → Normalized")
    for orig, norm in zip(sample_scores, normalized):
        confidence_level = "High" if norm > 0.8 else "Medium" if norm > 0.5 else "Low"
        print(f"   {orig:6.2f}    → {norm:.3f} ({confidence_level})")


if __name__ == "__main__":
    # Show sample transformation first
    show_sample_transformation()
    print()
    
    # Process all files
    process_all_tracking_results()
