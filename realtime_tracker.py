#!/usr/bin/env python3
"""
Real-time AB3DMOT Tracker Wrapper

This script provides a simple interface for using AB3DMOT in real-time tracking scenarios.
Input detections are processed immediately and tracking results are returned.

Usage Example:
    from realtime_tracker import RealtimeTracker
    
    # Initialize tracker
    tracker = RealtimeTracker(
        dataset='KITTI',
        det_name='pointrcnn',
        category='Car'
    )
    
    # Process detections for each frame
    for frame_idx, detections in enumerate(detection_stream):
        results = tracker.track_frame(detections, frame_idx)
        # results is a numpy array: N x 15 [h,w,l,x,y,z,theta,ID,ori,type_id,bbox2d(4),conf]
        for obj in results:
            track_id = int(obj[7])
            bbox_3d = obj[0:7]  # h,w,l,x,y,z,theta
            confidence = obj[14]
            print(f"Track ID: {track_id}, 3D BBox: {bbox_3d}, Confidence: {confidence}")
"""

import numpy as np
import yaml
import os
from easydict import EasyDict as edict
from AB3DMOT_libs.model import AB3DMOT


class RealtimeTracker:
    """
    Real-time wrapper for AB3DMOT tracker.
    
    This class provides a simplified interface for real-time 3D object tracking.
    It maintains internal state and processes detections frame-by-frame.
    """
    
    def __init__(self, dataset='KITTI', det_name='pointrcnn', category='Car', 
                 config_override=None, ID_init=0):
        """
        Initialize the real-time tracker.
        
        Args:
            dataset (str): Dataset name ('KITTI' or 'nuScenes')
            det_name (str): Detector name (e.g., 'pointrcnn', 'pvrcnn', 'centerpoint', 'megvii')
            category (str): Object category to track (e.g., 'Car', 'Pedestrian', 'Cyclist')
            config_override (dict): Optional dictionary to override default config parameters
            ID_init (int): Initial ID counter for tracks (default: 0)
        """
        self.dataset = dataset
        self.det_name = det_name
        self.category = category
        self.frame_count = 0
        
        # Load and setup configuration
        self.cfg = self._load_config(dataset, det_name, config_override)
        
        # Initialize the AB3DMOT tracker
        self.tracker = AB3DMOT(
            cfg=self.cfg,
            cat=category,
            calib=None,  # No calibration needed for basic tracking
            oxts=None,   # No ego motion compensation in basic mode
            img_dir=None,
            vis_dir=None,
            hw=None,
            log=None,
            ID_init=ID_init
        )
        
        # Detection ID to string mapping
        if dataset == 'KITTI':
            self.det_id2str = {1: 'Pedestrian', 2: 'Car', 3: 'Cyclist'}
        elif dataset == 'nuScenes':
            self.det_id2str = {
                1: 'Pedestrian', 2: 'Car', 3: 'Bicycle', 4: 'Motorcycle', 
                5: 'Bus', 6: 'Trailer', 7: 'Truck', 8: 'Construction_vehicle', 
                9: 'Barrier', 10: 'Traffic_cone'
            }
        else:
            raise ValueError(f"Unknown dataset: {dataset}")
        
        print(f"[RealtimeTracker] Initialized for {dataset}/{det_name}/{category}")
        print(f"[RealtimeTracker] Tracking algorithm: {self.tracker.algm}")
        print(f"[RealtimeTracker] Distance metric: {self.tracker.metric}")
        print(f"[RealtimeTracker] Threshold: {self.tracker.thres}")
        print(f"[RealtimeTracker] Min hits: {self.tracker.min_hits}")
        print(f"[RealtimeTracker] Max age: {self.tracker.max_age}")
    
    def _load_config(self, dataset, det_name, config_override=None):
        """Load configuration from YAML file or use defaults."""
        # Try to load from config file
        config_path = f'./configs/{dataset}.yml'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = edict(yaml.safe_load(f))
        else:
            # Use minimal default configuration
            cfg = edict({
                'dataset': dataset,
                'det_name': det_name,
                'ego_com': False,  # Disable ego motion compensation by default
                'vis': False,
                'affi_pro': True,
                'num_hypo': 1,
                'score_threshold': -10000
            })
        
        # Override with provided parameters
        cfg.dataset = dataset
        cfg.det_name = det_name
        
        if config_override:
            for key, value in config_override.items():
                cfg[key] = value
        
        return cfg
    
    def track_frame(self, dets, frame_idx=None, additional_info=None):
        """
        Process detections for a single frame and return tracking results.
        
        Args:
            dets (np.ndarray): Detection array of shape (N, 7) or (N, 8)
                               Format: [h, w, l, x, y, z, theta] or [h, w, l, x, y, z, theta, score]
                               - h, w, l: height, width, length of 3D bounding box
                               - x, y, z: center coordinates in camera/LiDAR coordinate system
                               - theta: rotation angle around vertical axis
                               - score (optional): detection confidence score
            frame_idx (int): Frame index (if None, uses internal counter)
            additional_info (np.ndarray): Optional additional info (N, 7) 
                                          [orientation, bbox_2d (4 values), score]
                                          If None, will be generated with default values
        
        Returns:
            np.ndarray: Tracking results of shape (M, 15) where M <= N
                        Format: [h, w, l, x, y, z, theta, ID, ori, type_id, bbox2d(4), conf]
                        - First 7 values: 3D bounding box (same as input)
                        - ID: Track ID (integer)
                        - ori: Orientation
                        - type_id: Object type ID
                        - bbox2d: 2D bounding box (4 values)
                        - conf: Confidence score
        """
        if frame_idx is None:
            frame_idx = self.frame_count
        
        # Handle empty detections
        if len(dets) == 0 or (isinstance(dets, np.ndarray) and dets.shape[0] == 0):
            dets = np.empty((0, 7))
            additional_info = np.empty((0, 7))
        else:
            # Ensure dets is numpy array
            dets = np.array(dets)
            
            # Handle case where score is included in detections
            if dets.shape[1] == 8:
                scores = dets[:, 7:8]
                dets = dets[:, :7]
            elif dets.shape[1] == 7:
                scores = np.ones((dets.shape[0], 1))  # Default score of 1.0
            else:
                raise ValueError(f"Invalid detection shape: {dets.shape}. Expected (N, 7) or (N, 8)")
            
            # Generate additional_info if not provided
            if additional_info is None:
                N = dets.shape[0]
                ori_array = dets[:, 6:7]  # Use theta as orientation
                bbox_2d = np.zeros((N, 4))  # Default 2D bbox (will not be used in tracking)
                type_id = self._get_type_id()  # Get type ID for current category
                additional_info = np.concatenate([
                    ori_array, 
                    bbox_2d, 
                    np.full((N, 1), type_id),
                    scores
                ], axis=1)
            else:
                additional_info = np.array(additional_info)
        
        # Prepare input in the format expected by tracker.track()
        dets_all = {
            'dets': dets,  # (N, 7): [h, w, l, x, y, z, theta]
            'info': additional_info  # (N, 7): [ori, bbox2d(4), type_id, score]
        }
        
        # Run tracking
        results, affinity = self.tracker.track(dets_all, frame_idx, seq_name='realtime')
        
        # Increment internal frame counter
        self.frame_count += 1
        
        # Extract results (results is a list with one element for single hypothesis)
        if len(results) > 0 and len(results[0]) > 0:
            tracking_results = results[0]  # Shape: (M, 15)
        else:
            tracking_results = np.empty((0, 15))
        
        return tracking_results
    
    def _get_type_id(self):
        """Get type ID for current category."""
        for type_id, type_name in self.det_id2str.items():
            if type_name == self.category:
                return type_id
        return 2  # Default to 'Car' if not found
    
    def get_active_tracks(self):
        """
        Get currently active tracks.
        
        Returns:
            list: List of active track IDs
        """
        return [trk.id for trk in self.tracker.trackers]
    
    def get_track_count(self):
        """
        Get the total number of tracks created so far.
        
        Returns:
            int: Total track count
        """
        return self.tracker.ID_count[0]
    
    def reset(self):
        """Reset the tracker state (clear all tracks)."""
        self.tracker.trackers = []
        self.tracker.frame_count = 0
        self.frame_count = 0
        print(f"[RealtimeTracker] Tracker reset")


def main():
    """Example usage of the RealtimeTracker."""
    
    print("=" * 80)
    print("AB3DMOT Real-time Tracker Demo")
    print("=" * 80)
    
    # Initialize tracker for car detection
    tracker = RealtimeTracker(
        dataset='KITTI',
        det_name='pointrcnn',
        category='Car'
    )
    
    print("\n" + "=" * 80)
    print("Example 1: Processing synthetic detections")
    print("=" * 80)
    
    # Simulate detection stream
    # Format: [h, w, l, x, y, z, theta]
    detection_stream = [
        # Frame 0: 2 cars detected
        np.array([
            [1.5, 1.8, 4.5, 10.0, 0.0, 30.0, 0.1],  # Car 1
            [1.6, 1.9, 4.8, 15.0, 0.0, 35.0, 0.2],  # Car 2
        ]),
        # Frame 1: Same cars, slightly moved
        np.array([
            [1.5, 1.8, 4.5, 10.2, 0.0, 29.5, 0.1],  # Car 1 moved
            [1.6, 1.9, 4.8, 15.1, 0.0, 34.8, 0.2],  # Car 2 moved
        ]),
        # Frame 2: Same cars + new detection
        np.array([
            [1.5, 1.8, 4.5, 10.4, 0.0, 29.0, 0.1],  # Car 1
            [1.6, 1.9, 4.8, 15.2, 0.0, 34.6, 0.2],  # Car 2
            [1.5, 1.7, 4.3, 8.0, 0.0, 25.0, 0.0],   # Car 3 (new)
        ]),
        # Frame 3: One car disappeared
        np.array([
            [1.5, 1.8, 4.5, 10.6, 0.0, 28.5, 0.1],  # Car 1
            [1.5, 1.7, 4.3, 8.1, 0.0, 24.8, 0.0],   # Car 3
        ]),
    ]
    
    # Process each frame
    for frame_idx, dets in enumerate(detection_stream):
        print(f"\n--- Frame {frame_idx} ---")
        print(f"Input: {len(dets)} detections")
        
        # Track
        results = tracker.track_frame(dets, frame_idx)
        
        print(f"Output: {len(results)} tracks")
        for obj in results:
            track_id = int(obj[7])
            bbox_3d = obj[0:7]  # h, w, l, x, y, z, theta
            confidence = obj[14]
            print(f"  Track ID {track_id}: bbox={bbox_3d}, conf={confidence:.3f}")
        
        print(f"Active tracks: {tracker.get_active_tracks()}")
    
    print("\n" + "=" * 80)
    print("Example 2: Processing with detection scores")
    print("=" * 80)
    
    # Reset tracker
    tracker.reset()
    
    # Detections with scores: [h, w, l, x, y, z, theta, score]
    dets_with_scores = np.array([
        [1.5, 1.8, 4.5, 10.0, 0.0, 30.0, 0.1, 0.95],  # High confidence
        [1.6, 1.9, 4.8, 15.0, 0.0, 35.0, 0.2, 0.87],  # High confidence
        [1.4, 1.7, 4.2, 20.0, 0.0, 40.0, 0.3, 0.45],  # Low confidence
    ])
    
    results = tracker.track_frame(dets_with_scores)
    
    print(f"\nProcessed {len(dets_with_scores)} detections with scores")
    print(f"Output: {len(results)} tracks")
    for obj in results:
        track_id = int(obj[7])
        confidence = obj[14]
        print(f"  Track ID {track_id}: confidence={confidence:.3f}")
    
    print("\n" + "=" * 80)
    print("Example 3: Empty frame handling")
    print("=" * 80)
    
    # Process empty frame
    empty_dets = np.empty((0, 7))
    results = tracker.track_frame(empty_dets)
    print(f"Empty frame: {len(results)} tracks output")
    print(f"Active tracks: {tracker.get_active_tracks()}")
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total frames processed: {tracker.frame_count}")
    print(f"Total tracks created: {tracker.get_track_count()}")
    print(f"Currently active tracks: {len(tracker.get_active_tracks())}")
    
    print("\n" + "=" * 80)
    print("Example 4: Multi-category tracking")
    print("=" * 80)
    
    # Initialize trackers for different categories
    trackers = {
        'Car': RealtimeTracker(dataset='KITTI', det_name='pointrcnn', category='Car', ID_init=0),
        'Pedestrian': RealtimeTracker(dataset='KITTI', det_name='pointrcnn', category='Pedestrian', ID_init=1000),
        'Cyclist': RealtimeTracker(dataset='KITTI', det_name='pointrcnn', category='Cyclist', ID_init=2000),
    }
    
    # Simulate detections for each category
    car_dets = np.array([[1.5, 1.8, 4.5, 10.0, 0.0, 30.0, 0.1]])
    ped_dets = np.array([[1.7, 0.6, 0.8, 5.0, 0.0, 20.0, 0.0]])
    cyclist_dets = np.array([[1.6, 0.8, 1.8, 8.0, 0.0, 25.0, 0.2]])
    
    all_results = []
    for category, dets in [('Car', car_dets), ('Pedestrian', ped_dets), ('Cyclist', cyclist_dets)]:
        results = trackers[category].track_frame(dets)
        all_results.append(results)
        if len(results) > 0:
            print(f"{category}: Track ID {int(results[0][7])}")
    
    print("\nMulti-category tracking demo complete!")
    print(f"Total tracks across all categories: {sum(t.get_track_count() for t in trackers.values())}")


if __name__ == '__main__':
    main()


