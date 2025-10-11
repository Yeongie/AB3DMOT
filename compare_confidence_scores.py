#!/usr/bin/env python3
"""
Visual tool to compare confidence scores between PointRCNN detection files and CSV output
"""

import csv
import pandas as pd

def load_detection_file(file_path):
    """Load PointRCNN detection file and return structured data"""
    detections = []
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            fields = line.strip().split(',')
            if len(fields) >= 15:
                detections.append({
                    'line': line_num,
                    'frame': int(fields[0]),
                    'confidence': float(fields[6]),
                    'x_3d': round(float(fields[10]), 4),
                    'y_3d': round(float(fields[11]), 4),
                    'z_3d': round(float(fields[12]), 4)
                })
    return detections

def load_csv_file(file_path):
    """Load CSV tracking results"""
    results = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 2):  # Start at 2 because of header
            results.append({
                'csv_row': row_num,
                'frame': int(row['frame']),
                'track_id': int(row['track_id']),
                'confidence_raw': float(row['confidence_score_raw']),
                'confidence_norm': float(row['confidence_score']),
                'x_3d': round(float(row['x_3d']), 4),
                'y_3d': round(float(row['y_3d']), 4),
                'z_3d': round(float(row['z_3d']), 4)
            })
    return results

def find_exact_matches(detections, csv_results):
    """Find exact matches between detection and CSV files"""
    matches = []
    
    for det in detections:
        for csv_row in csv_results:
            # Match by frame and 3D position (with small tolerance for floating point)
            if (det['frame'] == csv_row['frame'] and
                abs(det['x_3d'] - csv_row['x_3d']) < 0.01 and
                abs(det['y_3d'] - csv_row['y_3d']) < 0.01 and
                abs(det['z_3d'] - csv_row['z_3d']) < 0.01):
                
                matches.append({
                    'detection': det,
                    'csv': csv_row,
                    'confidence_match': abs(det['confidence'] - csv_row['confidence_raw']) < 0.0001
                })
                break
    
    return matches

def display_matches(matches, show_count=10):
    """Display matches in a readable format"""
    print("🔍 CONFIDENCE SCORE MATCHING VISUALIZATION")
    print("=" * 80)
    print()
    
    print("📋 HOW TO READ THIS:")
    print("   • Left side: Original PointRCNN detection file")
    print("   • Right side: Final CSV output file")
    print("   • Position: 3D coordinates (X, Y, Z) used for matching")
    print("   • Confidence: Raw score comparison")
    print()
    print("=" * 80)
    
    for i, match in enumerate(matches[:show_count]):
        det = match['detection']
        csv_row = match['csv']
        
        print(f"🎯 MATCH #{i+1}:")
        print(f"   Frame: {det['frame']}")
        print(f"   Position: ({det['x_3d']}, {det['y_3d']}, {det['z_3d']})")
        print()
        print(f"   📄 Detection File (Line {det['line']}):")
        print(f"      Confidence: {det['confidence']}")
        print()
        print(f"   📊 CSV File (Row {csv_row['csv_row']}, Track ID {csv_row['track_id']}):")
        print(f"      Confidence Raw:  {csv_row['confidence_raw']}")
        print(f"      Confidence Norm: {csv_row['confidence_norm']:.4f}")
        print()
        
        if match['confidence_match']:
            print(f"   ✅ CONFIDENCE SCORES MATCH! ({det['confidence']} = {csv_row['confidence_raw']})")
        else:
            print(f"   ❌ Confidence scores differ: {det['confidence']} ≠ {csv_row['confidence_raw']}")
        
        print("-" * 80)
    
    if len(matches) > show_count:
        print(f"... and {len(matches) - show_count} more matches")
    
    print()
    print("📊 SUMMARY:")
    exact_matches = sum(1 for m in matches if m['confidence_match'])
    print(f"   Total matches found: {len(matches)}")
    print(f"   Exact confidence matches: {exact_matches}")
    print(f"   Different confidence: {len(matches) - exact_matches}")
    
    if exact_matches == len(matches):
        print("   🎉 ALL CONFIDENCE SCORES ARE IDENTICAL!")
    else:
        print("   ⚠️  Some confidence scores differ")

def show_sample_data(detections, csv_results):
    """Show sample data from both files for comparison"""
    print("\n📄 SAMPLE DATA COMPARISON:")
    print("=" * 80)
    
    print("\n🔍 Original PointRCNN Detection File (first 5 lines):")
    print("Line | Frame | Confidence |    X_3D    |    Y_3D    |    Z_3D")
    print("-" * 60)
    for i, det in enumerate(detections[:5]):
        print(f"{det['line']:4d} | {det['frame']:5d} | {det['confidence']:10.4f} | {det['x_3d']:10.4f} | {det['y_3d']:10.4f} | {det['z_3d']:7.2f}")
    
    print("\n📊 Final CSV Output File (first 5 rows):")
    print("Row  | Frame | Track | Conf_Raw   | Conf_Norm  |    X_3D    |    Y_3D    |    Z_3D")
    print("-" * 80)
    for i, csv_row in enumerate(csv_results[:5]):
        print(f"{csv_row['csv_row']:4d} | {csv_row['frame']:5d} | {csv_row['track_id']:5d} | {csv_row['confidence_raw']:10.4f} | {csv_row['confidence_norm']:10.4f} | {csv_row['x_3d']:10.4f} | {csv_row['y_3d']:10.4f} | {csv_row['z_3d']:7.2f}")

def main():
    print("🔬 Confidence Score Matching Tool")
    print("=" * 50)
    
    # File paths
    detection_file = "data/KITTI/detection/pointrcnn_Car_val/0001.txt"
    csv_file = "results/KITTI/pointrcnn_Car_val_H1/tracking_results_H0_0001.csv"
    
    try:
        print("📂 Loading files...")
        detections = load_detection_file(detection_file)
        csv_results = load_csv_file(csv_file)
        
        print(f"   ✅ Loaded {len(detections)} detections from PointRCNN file")
        print(f"   ✅ Loaded {len(csv_results)} results from CSV file")
        
        # Show sample data
        show_sample_data(detections, csv_results)
        
        # Find matches
        print("\n🔗 Finding exact matches...")
        matches = find_exact_matches(detections, csv_results)
        
        # Display results
        display_matches(matches, show_count=5)
        
        print("\n💡 TIP: Look for the same 3D position (X, Y, Z) to find matching objects!")
        print("     The confidence scores should be identical for the same object.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file - {e}")
        print("   Make sure you've run AB3DMOT with --export_csv first")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

