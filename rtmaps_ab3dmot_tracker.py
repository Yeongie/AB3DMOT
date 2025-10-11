# ---------------- AB3DMOT RTMaps Component -------------------
# RTMaps Python Bridge component for AB3DMOT 3D Multi-Object Tracking
# 
# This component integrates AB3DMOT tracker into RTMaps for real-time 3D object tracking.
# 
# Input format: Detection data with format similar to dets_all
#   - Expects structured data with 'dets' and 'info' fields, or numpy array
# 
# Output format: Tracking results [h, w, l, x, y, z, theta, ID, ori, type_id, bbox2d(4), conf]
#
# Author: RTMaps AB3DMOT Bridge
# Based on AB3DMOT by Xinshuo Weng

import rtmaps.types
import rtmaps.core
import numpy as np
import os
import sys
from rtmaps.base_component import BaseComponent

# Add AB3DMOT to path if needed
# Adjust this path to your AB3DMOT installation
AB3DMOT_PATH = os.path.dirname(os.path.abspath(__file__))
if AB3DMOT_PATH not in sys.path:
    sys.path.insert(0, AB3DMOT_PATH)

from realtime_tracker import RealtimeTracker


# Python class that will be called from RTMaps
class rtmaps_python(BaseComponent):
    """
    RTMaps component for AB3DMOT 3D Multi-Object Tracking.
    
    This component receives detection data and outputs tracked objects with persistent IDs.
    """
    
    def __init__(self):
        BaseComponent.__init__(self)  # call base class constructor
        self.tracker = None
        self.frame_count = 0
        
    def Dynamic(self):
        """Define inputs, outputs, and properties."""
        # Input: Detection data
        # Expected format: numpy array or structured data with 'dets' and 'info' fields
        self.add_input("detections", rtmaps.types.ANY)
        
        # Optional: Frame index input (if not provided, uses internal counter)
        self.add_input("frame_idx", rtmaps.types.INTEGER32)
        
        # Output: Tracking results as numpy array
        # Format: [h, w, l, x, y, z, theta, ID, ori, type_id, bbox2d(4), conf]
        self.add_output("tracks", rtmaps.types.AUTO)
        
        # Output: Number of active tracks
        self.add_output("num_tracks", rtmaps.types.INTEGER32)
        
        # Output: Active track IDs
        self.add_output("track_ids", rtmaps.types.AUTO)
        
        # Properties for configuration
        self.add_property("dataset", "KITTI", 
                         description="Dataset type (KITTI or nuScenes)")
        self.add_property("det_name", "pointrcnn",
                         description="Detector name (pointrcnn, pvrcnn, centerpoint, megvii)")
        self.add_property("category", "Car",
                         description="Object category to track (Car, Pedestrian, Cyclist, etc.)")
        self.add_property("ID_init", 0,
                         description="Initial track ID counter")
        self.add_property("enable_ego_motion", False,
                         description="Enable ego motion compensation (requires calibration)")
        self.add_property("verbose", False,
                         description="Enable verbose logging")
        
    def Birth(self):
        """Initialize the AB3DMOT tracker once at startup."""
        # Get properties
        dataset = self.get_property("dataset").data
        det_name = self.get_property("det_name").data
        category = self.get_property("category").data
        ID_init = int(self.get_property("ID_init").data)
        enable_ego_motion = bool(self.get_property("enable_ego_motion").data)
        self.verbose = bool(self.get_property("verbose").data)
        
        # Report initialization
        rtmaps.core.report_info(f"[AB3DMOT] Initializing tracker...")
        rtmaps.core.report_info(f"[AB3DMOT]   Dataset: {dataset}")
        rtmaps.core.report_info(f"[AB3DMOT]   Detector: {det_name}")
        rtmaps.core.report_info(f"[AB3DMOT]   Category: {category}")
        rtmaps.core.report_info(f"[AB3DMOT]   ID Init: {ID_init}")
        
        try:
            # Initialize the tracker
            config_override = {
                'ego_com': enable_ego_motion,
                'vis': False,  # Disable visualization in RTMaps
                'affi_pro': True,
            }
            
            self.tracker = RealtimeTracker(
                dataset=dataset,
                det_name=det_name,
                category=category,
                config_override=config_override,
                ID_init=ID_init
            )
            
            self.frame_count = 0
            
            rtmaps.core.report_info(f"[AB3DMOT] Tracker initialized successfully!")
            rtmaps.core.report_info(f"[AB3DMOT]   Algorithm: {self.tracker.tracker.algm}")
            rtmaps.core.report_info(f"[AB3DMOT]   Metric: {self.tracker.tracker.metric}")
            rtmaps.core.report_info(f"[AB3DMOT]   Threshold: {self.tracker.tracker.thres}")
            
        except Exception as e:
            rtmaps.core.report_error(f"[AB3DMOT] Failed to initialize tracker: {str(e)}")
            raise
    
    def Core(self):
        """Process incoming detections and output tracking results."""
        try:
            # Get input data
            detections_ioelt = self.inputs["detections"].ioelt
            
            # Extract timestamp
            timestamp = detections_ioelt.ts
            
            # Get frame index (use input if available, otherwise use internal counter)
            if self.inputs["frame_idx"].has_data:
                frame_idx = int(self.inputs["frame_idx"].ioelt.data)
            else:
                frame_idx = self.frame_count
            
            # Parse detection data
            dets_data = self._parse_detection_input(detections_ioelt.data)
            
            if self.verbose:
                rtmaps.core.report_info(f"[AB3DMOT] Frame {frame_idx}: {len(dets_data['dets'])} detections")
            
            # Run tracking
            tracking_results = self.tracker.track_frame(
                dets=dets_data['dets'],
                frame_idx=frame_idx,
                additional_info=dets_data['info']
            )
            
            # Get active tracks information
            active_track_ids = self.tracker.get_active_tracks()
            num_tracks = len(tracking_results)
            
            if self.verbose and num_tracks > 0:
                rtmaps.core.report_info(f"[AB3DMOT] Frame {frame_idx}: {num_tracks} tracks output")
                for obj in tracking_results:
                    track_id = int(obj[7])
                    conf = obj[14]
                    rtmaps.core.report_info(f"[AB3DMOT]   Track {track_id}: conf={conf:.3f}")
            
            # Create output IOElts
            # 1. Tracking results
            tracks_output = rtmaps.types.Ioelt()
            tracks_output.ts = timestamp
            tracks_output.data = tracking_results
            self.outputs["tracks"].write(tracks_output)
            
            # 2. Number of tracks
            num_tracks_output = rtmaps.types.Ioelt()
            num_tracks_output.ts = timestamp
            num_tracks_output.data = num_tracks
            self.outputs["num_tracks"].write(num_tracks_output)
            
            # 3. Active track IDs
            track_ids_output = rtmaps.types.Ioelt()
            track_ids_output.ts = timestamp
            track_ids_output.data = np.array(active_track_ids, dtype=np.int32)
            self.outputs["track_ids"].write(track_ids_output)
            
            # Increment frame counter
            self.frame_count += 1
            
        except Exception as e:
            rtmaps.core.report_error(f"[AB3DMOT] Error in Core(): {str(e)}")
            # Output empty results on error
            empty_output = rtmaps.types.Ioelt()
            empty_output.ts = self.inputs["detections"].ioelt.ts
            empty_output.data = np.empty((0, 15))
            self.outputs["tracks"].write(empty_output)
    
    def _parse_detection_input(self, input_data):
        """
        Parse input detection data into the format expected by AB3DMOT.
        
        Supports multiple input formats:
        1. Dictionary with 'dets' and 'info' keys (preferred)
        2. Numpy array (N, 7) or (N, 8): [h, w, l, x, y, z, theta] or with score
        3. Numpy array (N, 15): Full detection format [frame, 2d_bbox(4), h, w, l, x, y, z, theta, score]
        
        Returns:
            dict: {'dets': numpy array (N, 7), 'info': numpy array (N, 7)}
        """
        # Case 1: Already in dets_all format (dictionary)
        if isinstance(input_data, dict):
            if 'dets' in input_data and 'info' in input_data:
                dets = np.array(input_data['dets'])
                info = np.array(input_data['info'])
                
                # Ensure correct shape
                if len(dets.shape) == 1:
                    dets = dets.reshape(1, -1)
                if len(info.shape) == 1:
                    info = info.reshape(1, -1)
                
                return {'dets': dets, 'info': info}
        
        # Case 2: Numpy array input
        if isinstance(input_data, np.ndarray):
            # Handle empty array
            if input_data.shape[0] == 0:
                return {
                    'dets': np.empty((0, 7)),
                    'info': np.empty((0, 7))
                }
            
            # Ensure 2D array
            if len(input_data.shape) == 1:
                input_data = input_data.reshape(1, -1)
            
            N = input_data.shape[0]
            
            # Format: (N, 7) - [h, w, l, x, y, z, theta]
            if input_data.shape[1] == 7:
                dets = input_data
                info = self._generate_default_info(N, dets)
                return {'dets': dets, 'info': info}
            
            # Format: (N, 8) - [h, w, l, x, y, z, theta, score]
            elif input_data.shape[1] == 8:
                dets = input_data[:, :7]
                scores = input_data[:, 7:8]
                info = self._generate_default_info(N, dets, scores)
                return {'dets': dets, 'info': info}
            
            # Format: (N, 15) - KITTI detection format
            # [frame, 2d_bbox(4), h, w, l, x, y, z, theta, score]
            elif input_data.shape[1] == 15:
                dets = input_data[:, 6:13]  # [h, w, l, x, y, z, theta]
                scores = input_data[:, 14:15]
                info = np.concatenate([
                    input_data[:, 13:14],  # ori (theta)
                    input_data[:, 1:5],    # 2d bbox
                    np.full((N, 1), self.tracker._get_type_id()),  # type_id
                    scores
                ], axis=1)
                return {'dets': dets, 'info': info}
            
            else:
                rtmaps.core.report_warning(
                    f"[AB3DMOT] Unexpected input shape: {input_data.shape}. "
                    f"Expected (N, 7), (N, 8), or (N, 15). Using first 7 columns."
                )
                dets = input_data[:, :7]
                info = self._generate_default_info(N, dets)
                return {'dets': dets, 'info': info}
        
        # Case 3: Unknown format - try to convert
        rtmaps.core.report_warning(
            f"[AB3DMOT] Unknown input format: {type(input_data)}. "
            f"Attempting conversion to numpy array."
        )
        try:
            arr = np.array(input_data)
            return self._parse_detection_input(arr)
        except:
            # Return empty detections
            rtmaps.core.report_error(
                f"[AB3DMOT] Failed to parse input data. Returning empty detections."
            )
            return {
                'dets': np.empty((0, 7)),
                'info': np.empty((0, 7))
            }
    
    def _generate_default_info(self, N, dets, scores=None):
        """
        Generate default additional info for detections.
        
        Args:
            N: Number of detections
            dets: Detection array (N, 7)
            scores: Optional scores (N, 1)
        
        Returns:
            numpy array (N, 7): [ori, bbox2d(4), type_id, score]
        """
        if scores is None:
            scores = np.ones((N, 1))
        
        ori_array = dets[:, 6:7]  # Use theta as orientation
        bbox_2d = np.zeros((N, 4))  # Default 2D bbox
        type_id = self.tracker._get_type_id()
        
        info = np.concatenate([
            ori_array,
            bbox_2d,
            np.full((N, 1), type_id),
            scores
        ], axis=1)
        
        return info
    
    def Death(self):
        """Cleanup when the component shuts down."""
        if self.tracker is not None:
            rtmaps.core.report_info(
                f"[AB3DMOT] Shutting down. "
                f"Total frames: {self.frame_count}, "
                f"Total tracks created: {self.tracker.get_track_count()}"
            )
            self.tracker = None


