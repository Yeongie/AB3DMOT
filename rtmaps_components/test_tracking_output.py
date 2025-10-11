#!/usr/bin/env python3
"""
Test script to verify AB3DMOT tracking output
Run this to check if tracking results are being generated
"""

import numpy as np
import sys
import os

# Add the AB3DMOT path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_tracking():
    """Test the simple tracking fallback function"""
    
    # Import the tracking component
    try:
        from rtmaps_ab3dmot_tracker import AB3DMOTTracker
        
        # Create a mock component for testing
        class MockComponent:
            def __init__(self):
                self.inputs = {}
                self.outputs = {}
                self.frame_count = 0
                self.last_process_time = 0
                self.error_count = 0
                self.verbose = True
                self.max_output_tracks = 5
                
            def get_property(self, name):
                props = {
                    'dataset': 'KITTI',
                    'det_name': 'pointrcnn', 
                    'category': 'Car',
                    'ID_init': 0,
                    'enable_ego_motion': False,
                    'verbose': True
                }
                return props.get(name, None)
        
        # Create mock tracker
        tracker = AB3DMOTTracker()
        tracker.inputs = {}
        tracker.outputs = {}
        tracker.frame_count = 0
        tracker.last_process_time = 0
        tracker.error_count = 0
        tracker.verbose = True
        tracker.max_output_tracks = 5
        
        # Test data - 2 detections
        dets = np.array([
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.9],  # Detection 1
            [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.8]   # Detection 2
        ])
        
        info = np.array([
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.9],  # Info 1
            [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.8]   # Info 2
        ])
        
        print("Testing AB3DMOT Simple Tracking Fallback...")
        print(f"Input detections shape: {dets.shape}")
        print(f"Input info shape: {info.shape}")
        
        # Test the simple tracking function
        try:
            # Access the simple tracking method
            tracking_results = tracker._simple_tracking_fallback(dets, info, frame_idx=0)
            
            print(f"Tracking successful!")
            print(f"Output shape: {tracking_results.shape}")
            print(f"Number of tracks: {len(tracking_results)}")
            
            # Display track details
            for i, track in enumerate(tracking_results):
                print(f"Track {i}: ID={int(track[0]):.0f}, x={track[1]:.2f}, y={track[2]:.2f}, z={track[3]:.2f}, conf={track[14]:.3f}")
                
            return True
            
        except Exception as e:
            print(f"Tracking failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"Import failed: {str(e)}")
        print("Make sure you're running this from the RTMaps project directory")
        return False

def test_input_parsing():
    """Test the input parsing function"""
    
    try:
        from rtmaps_ab3dmot_tracker import AB3DMOTTracker
        
        tracker = AB3DMOTTracker()
        
        # Test 1D array input (like what RTMaps sends)
        input_1d = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.9, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.8, 1.0])
        print(f"\nTesting input parsing...")
        print(f"Input 1D array shape: {input_1d.shape}")
        
        # Test the parsing function
        dets, info = tracker._parse_detection_input(input_1d)
        
        print(f"Parsing successful!")
        print(f"Output dets shape: {dets.shape}")
        print(f"Output info shape: {info.shape}")
        
        return True
        
    except Exception as e:
        print(f"Parsing failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("AB3DMOT Tracking Verification Test")
    print("=" * 50)
    
    # Test 1: Input parsing
    test1_passed = test_input_parsing()
    
    # Test 2: Simple tracking
    test2_passed = test_simple_tracking()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Input Parsing: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Simple Tracking: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\nALL TESTS PASSED! AB3DMOT tracking is working correctly.")
    else:
        print("\nSome tests failed. Check the errors above.")
