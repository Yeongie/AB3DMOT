#!/usr/bin/env python3
"""
Simple tool to visually compare confidence scores
"""

import csv

def main():
    print("🔍 CONFIDENCE SCORE VISUAL COMPARISON")
    print("=" * 60)
    
    # Load original detection file
    print("\n📄 ORIGINAL POINTRCNN DETECTION FILE:")
    print("Line | Frame | Confidence |    X_3D    |    Y_3D    |    Z_3D")
    print("-" * 60)
    
    detections = []
    try:
        with open("data/KITTI/detection/pointrcnn_Car_val/0001.txt", 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > 10:  # Show first 10 lines only
                    break
                fields = line.strip().split(',')
                if len(fields) >= 15:
                    frame = int(fields[0])
                    conf = float(fields[6])
                    x = float(fields[10])
                    y = float(fields[11])
                    z = float(fields[12])
                    print(f"{line_num:4d} | {frame:5d} | {conf:10.4f} | {x:10.4f} | {y:10.4f} | {z:7.2f}")
                    detections.append((frame, conf, x, y, z))
    except Exception as e:
        print(f"Error reading detection file: {e}")
        return
    
    # Load CSV file
    print("\n📊 FINAL CSV OUTPUT FILE:")
    print("Row  | Frame | Track | Conf_Raw   | Conf_Norm  |    X_3D    |    Y_3D    |    Z_3D")
    print("-" * 80)
    
    csv_results = []
    try:
        with open("results/KITTI/pointrcnn_Car_val_H1/tracking_results_H0_0001.csv", 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 2):
                if row_num > 11:  # Show first 10 data rows (after header)
                    break
                frame = int(row['frame'])
                track_id = int(row['track_id'])
                conf_raw = float(row['confidence_score_raw'])
                conf_norm = float(row['confidence_score'])
                x = float(row['x_3d'])
                y = float(row['y_3d'])
                z = float(row['z_3d'])
                print(f"{row_num:4d} | {frame:5d} | {track_id:5d} | {conf_raw:10.4f} | {conf_norm:10.4f} | {x:10.4f} | {y:10.4f} | {z:7.2f}")
                csv_results.append((frame, conf_raw, x, y, z, track_id))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Find matches
    print("\n🎯 MATCHING OBJECTS (same 3D position):")
    print("=" * 80)
    
    matches_found = 0
    for det_frame, det_conf, det_x, det_y, det_z in detections:
        for csv_frame, csv_conf, csv_x, csv_y, csv_z, track_id in csv_results:
            # Check if positions match (within small tolerance)
            if (det_frame == csv_frame and 
                abs(det_x - csv_x) < 0.01 and 
                abs(det_y - csv_y) < 0.01 and 
                abs(det_z - csv_z) < 0.01):
                
                matches_found += 1
                conf_match = abs(det_conf - csv_conf) < 0.0001
                match_symbol = "✅" if conf_match else "❌"
                
                print(f"\n🎯 MATCH #{matches_found}:")
                print(f"   Frame {det_frame}, Position: ({det_x:.2f}, {det_y:.2f}, {det_z:.1f})")
                print(f"   📄 Detection File: Confidence = {det_conf}")
                print(f"   📊 CSV File:       Confidence = {csv_conf} (Track ID {track_id})")
                print(f"   {match_symbol} Confidence scores {'MATCH' if conf_match else 'DIFFER'}")
                
                if matches_found >= 5:  # Show first 5 matches
                    break
        if matches_found >= 5:
            break
    
    if matches_found == 0:
        print("   No exact matches found in first 10 lines.")
        print("   This is normal - tracking may change positions slightly.")
    
    print(f"\n📊 Found {matches_found} exact position matches in sample data")
    print("\n💡 HOW TO FIND MATCHES:")
    print("   1. Look for same Frame number")
    print("   2. Look for same 3D position (X, Y, Z coordinates)")
    print("   3. Compare the confidence values")
    print("   4. They should be identical!")

if __name__ == "__main__":
    main()

