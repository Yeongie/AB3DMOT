#!/usr/bin/env python3
"""
Setup script for AB3DMOT RTMaps integration
This script helps configure your RTMaps project directory with the AB3DMOT tracker
"""

import os
import shutil
import sys

def setup_rtmaps_project():
    """Setup RTMaps project directory with AB3DMOT components"""
    
    print("AB3DMOT RTMaps Project Setup")
    print("=" * 50)
    
    # Get RTMaps project directory
    rtmaps_project_dir = input("Enter your RTMaps project directory path (e.g., C:\\RTMaps_Projects\\AB3DMOT): ").strip()
    
    if not rtmaps_project_dir:
        print("❌ No directory specified. Exiting.")
        return False
    
    # Create directory if it doesn't exist
    if not os.path.exists(rtmaps_project_dir):
        try:
            os.makedirs(rtmaps_project_dir)
            print(f"✅ Created RTMaps project directory: {rtmaps_project_dir}")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
    
    # Get current script directory (where the components are)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to copy
    files_to_copy = [
        "rtmaps_ab3dmot_tracker.py",
        "simple_tracker_logger.py", 
        "test_tracking_output.py",
        "README.md"
    ]
    
    print(f"\n📁 Copying components from: {script_dir}")
    print(f"📁 To RTMaps project: {rtmaps_project_dir}")
    
    # Copy files
    for file_name in files_to_copy:
        source_path = os.path.join(script_dir, file_name)
        dest_path = os.path.join(rtmaps_project_dir, file_name)
        
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                print(f"✅ Copied: {file_name}")
            except Exception as e:
                print(f"❌ Failed to copy {file_name}: {e}")
        else:
            print(f"⚠️  Source file not found: {file_name}")
    
    print(f"\n🎉 Setup complete!")
    print(f"Your RTMaps project is ready at: {rtmaps_project_dir}")
    print("\nNext steps:")
    print("1. Open RTMaps Studio")
    print("2. Create a new project in the above directory")
    print("3. Add a PythonBridge component")
    print("4. Set the script to 'rtmaps_ab3dmot_tracker.py'")
    print("5. Connect your sensor components to the tracker inputs")
    
    return True

if __name__ == "__main__":
    setup_rtmaps_project()
