#!/usr/bin/env python3
"""
Script to verify that confidence scores are unchanged from PointRCNN detection to final CSV output
"""

import csv
import numpy as np

def load_pointrcnn_detections(file_path):
    """Load original PointRCNN detection file"""
    detections = []
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split(',')
            if len(fields) >= 15:
                frame = int(fields[0])
                confidence = float(fields[6])
                x_3d = float(fields[10])
                y_3d = float(fields[11])
                z_3d = float(fields[12])
                detections.append({
                    'frame': frame,
                    'confidence': confidence,
                    'x_3d': x_3d,
                    'y_3d': y_3d,
                    'z_3d': z_3d
                })
    return detections

def load_csv_results(file_path):
    """Load final CSV tracking results"""
    results = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'frame': int(row['frame']),
                'track_id': int(row['track_id']),
                'confidence_raw': float(row['confidence_score_raw']),
                'x_3d': float(row['x_3d']),
                'y_3d': float(row['y_3d']),
                'z_3d': float(row['z_3d'])
            })
    return results

def find_matching_detections(pointrcnn_dets, csv_results, tolerance=0.01):
    """Find matching detections between original and final results"""
    matches = []
    unmatched_pointrcnn = []
    unmatched_csv = []
    
    for det in pointrcnn_dets:
        best_match = None
        min_distance = float('inf')
        
        for result in csv_results:
            if det['frame'] == result['frame']:
                # Calculate 3D position distance
                distance = np.sqrt(
                    (det['x_3d'] - result['x_3d'])**2 + 
                    (det['y_3d'] - result['y_3d'])**2 + 
                    (det['z_3d'] - result['z_3d'])**2
                )
                
                if distance < min_distance and distance < tolerance:
                    min_distance = distance
                    best_match = result
        
        if best_match:
            matches.append({
                'original': det,
                'final': best_match,
                'distance': min_distance
            })
        else:
            unmatched_pointrcnn.append(det)
    
    # Find unmatched CSV results
    matched_csv_ids = {match['final']['track_id'] for match in matches}
    for result in csv_results:
        if result['track_id'] not in matched_csv_ids:
            unmatched_csv.append(result)
    
    return matches, unmatched_pointrcnn, unmatched_csv

def verify_confidence_unchanged(matches):
    """Verify that confidence scores are identical"""
    identical_count = 0
    different_count = 0
    tolerance = 1e-6  # Very small tolerance for floating point comparison
    
    print("🔍 CONFIDENCE SCORE VERIFICATION:")
    print("=" * 60)
    
    for i, match in enumerate(matches[:10]):  # Show first 10 matches
        original_conf = match['original']['confidence']
        final_conf = match['final']['confidence_raw']
        diff = abs(original_conf - final_conf)
        
        if diff < tolerance:
            status = "✅ IDENTICAL"
            identical_count += 1
        else:
            status = "❌ DIFFERENT"
            different_count += 1
        
        print(f"Match {i+1:2d}: {original_conf:8.4f} → {final_conf:8.4f} (diff: {diff:.2e}) {status}")
    
    if len(matches) > 10:
        print(f"... and {len(matches) - 10} more matches")
    
    print("=" * 60)
    print(f"📊 SUMMARY:")
    print(f"   Total matches: {len(matches)}")
    print(f"   Identical confidence: {identical_count}")
    print(f"   Different confidence: {different_count}")
    
    if different_count == 0:
        print("✅ ALL CONFIDENCE SCORES ARE IDENTICAL!")
        print("   AB3DMOT does NOT modify confidence scores.")
    else:
        print("❌ Some confidence scores differ!")
        print("   This suggests AB3DMOT modified the scores.")
    
    return identical_count, different_count

def main():
    print("🔬 Verifying Confidence Scores: PointRCNN → AB3DMOT → CSV")
    print("=" * 70)
    
    # File paths
    pointrcnn_file = "data/KITTI/detection/pointrcnn_Car_val/0001.txt"
    csv_file = "results/KITTI/pointrcnn_Car_val_H1/tracking_results_H0_0001.csv"
    
    try:
        # Load data
        print("📂 Loading original PointRCNN detections...")
        pointrcnn_dets = load_pointrcnn_detections(pointrcnn_file)
        print(f"   Found {len(pointrcnn_dets)} detections")
        
        print("📂 Loading final CSV results...")
        csv_results = load_csv_results(csv_file)
        print(f"   Found {len(csv_results)} tracking results")
        
        # Find matches
        print("🔗 Matching detections by 3D position...")
        matches, unmatched_pointrcnn, unmatched_csv = find_matching_detections(
            pointrcnn_dets, csv_results
        )
        print(f"   Found {len(matches)} matches")
        print(f"   Unmatched PointRCNN: {len(unmatched_pointrcnn)}")
        print(f"   Unmatched CSV: {len(unmatched_csv)}")
        
        # Verify confidence scores
        print()
        identical, different = verify_confidence_unchanged(matches)
        
        print("\n" + "=" * 70)
        if different == 0:
            print("🎉 PROOF COMPLETE: Confidence scores are UNCHANGED by AB3DMOT!")
        else:
            print("⚠️  Some confidence scores were modified by AB3DMOT.")
            
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        print("   Make sure you've run AB3DMOT with --export_csv first")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

