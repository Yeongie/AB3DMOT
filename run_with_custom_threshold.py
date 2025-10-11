#!/usr/bin/env python3
"""
Run AB3DMOT with custom confidence threshold
"""

import sys
import os
import shutil

def modify_threshold(new_threshold):
    """Temporarily modify the threshold in utils.py"""
    
    utils_file = "AB3DMOT_libs/utils.py"
    backup_file = "AB3DMOT_libs/utils.py.backup"
    
    # Create backup
    shutil.copy2(utils_file, backup_file)
    
    # Read original file
    with open(utils_file, 'r') as f:
        content = f.read()
    
    # Replace the threshold
    old_line = "if det_name == 'pointrcnn': return {'Car': 3.240738, 'Pedestrian': 2.683133, 'Cyclist': 3.645319}"
    new_line = f"if det_name == 'pointrcnn': return {{'Car': {new_threshold}, 'Pedestrian': 2.683133, 'Cyclist': 3.645319}}"
    
    modified_content = content.replace(old_line, new_line)
    
    # Write modified file
    with open(utils_file, 'w') as f:
        f.write(modified_content)
    
    print(f"✅ Modified threshold to {new_threshold}")
    return backup_file

def restore_threshold(backup_file):
    """Restore original threshold"""
    utils_file = "AB3DMOT_libs/utils.py"
    shutil.copy2(backup_file, utils_file)
    os.remove(backup_file)
    print("✅ Restored original threshold")

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_with_custom_threshold.py <threshold>")
        print()
        print("Examples:")
        print("  python run_with_custom_threshold.py 1.0    # Keep 80.7% (less filtering)")
        print("  python run_with_custom_threshold.py 0.0    # Keep 90.6% (much less filtering)")
        print("  python run_with_custom_threshold.py 5.0    # Keep 54.5% (more filtering)")
        print("  python run_with_custom_threshold.py -10.0  # Keep 100% (no filtering)")
        return
    
    try:
        threshold = float(sys.argv[1])
    except ValueError:
        print("Error: Threshold must be a number")
        return
    
    print(f"🎛️ Running AB3DMOT with custom threshold: {threshold}")
    print("=" * 60)
    
    # Modify threshold
    backup_file = modify_threshold(threshold)
    
    try:
        # Run AB3DMOT
        print("🚀 Running AB3DMOT...")
        os.system("python main.py --dataset KITTI --split val --export_csv")
        print("✅ AB3DMOT completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running AB3DMOT: {e}")
    
    finally:
        # Always restore original threshold
        restore_threshold(backup_file)
        print(f"🔄 Threshold restored to original value (3.240738)")

if __name__ == "__main__":
    main()


