#!/usr/bin/env python3
"""
Test tool to see how different thresholds affect filtering
"""

def analyze_threshold_impact(threshold):
    """Analyze how many detections would be kept with different thresholds"""
    
    # Load confidence scores
    scores = []
    try:
        with open("data/KITTI/detection/pointrcnn_Car_val/0001.txt", 'r') as f:
            for line in f:
                fields = line.strip().split(',')
                if len(fields) >= 15:
                    scores.append(float(fields[6]))
    except Exception as e:
        print(f"Error loading detection file: {e}")
        return
    
    total = len(scores)
    kept = len([s for s in scores if s >= threshold])
    filtered = total - kept
    kept_percent = (kept / total) * 100
    filtered_percent = (filtered / total) * 100
    
    return {
        'threshold': threshold,
        'total': total,
        'kept': kept,
        'filtered': filtered,
        'kept_percent': kept_percent,
        'filtered_percent': filtered_percent
    }

def main():
    print("🎛️ THRESHOLD IMPACT ANALYZER")
    print("=" * 50)
    print()
    
    # Test different thresholds
    thresholds = [-10.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.240738, 4.0, 5.0, 6.0, 8.0, 10.0]
    
    print("Threshold | Kept  | Filtered | Kept% | Filtered% | Impact")
    print("----------|-------|----------|-------|-----------|------------------")
    
    for threshold in thresholds:
        result = analyze_threshold_impact(threshold)
        
        if result:
            impact = ""
            if threshold == 3.240738:
                impact = "← CURRENT"
            elif threshold < 3.240738:
                impact = "LESS filtering"
            else:
                impact = "MORE filtering"
            
            print(f"{threshold:9.1f} | {result['kept']:5d} | {result['filtered']:8d} | {result['kept_percent']:5.1f} | {result['filtered_percent']:9.1f} | {impact}")
    
    print()
    print("💡 RECOMMENDATIONS:")
    print("   • For MORE detections (less safe):     Use threshold 1.0 or 0.0")
    print("   • For CURRENT balance:                 Keep threshold 3.24")
    print("   • For FEWER detections (more safe):    Use threshold 5.0 or higher")
    print()
    print("⚠️  TRADE-OFFS:")
    print("   • Lower threshold = More objects detected, but more false positives")
    print("   • Higher threshold = Fewer false positives, but might miss real objects")

if __name__ == "__main__":
    main()

