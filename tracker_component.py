import sys
# Add the RTMaps packages path to the system path
sys.path.append('C:/Program Files/Intempora/RTMaps 4/packages/rtmaps_python_bridge')

# AB3DMOT RTMaps Integration Guide

## Wrapping AB3DMOT into RTMaps

### 1. **Main RTMaps Wrapper Component**

from rtmaps.base_component import BaseComponent
import numpy as np
import sys
import os

# Add AB3DMOT path to Python path
sys.path.append('/path/to/AB3DMOT')  # Adjust to your AB3DMOT location

# Import the authors' implementation
from AB3DMOT_libs.model import AB3DMOT
from AB3DMOT_libs.utils import Config

class rtmaps_python(BaseComponent):
    def __init__(self):
        RTMapsComponent.__init__(self)
        
        # Define inputs
        self.add_input("detections_3d", "FLOAT32")  # 3D bounding boxes
        self.add_input("timestamp", "FLOAT64")      # Frame timestamp
        
        # Define outputs
        self.add_output("tracks_3d", "FLOAT32")     # Tracked objects
        self.add_output("track_ids", "INT32")        # Track IDs
        
        # Define properties for configuration
        self.add_property("max_age", 2)
        self.add_property("min_hits", 3)
        self.add_property("iou_threshold", 0.25)
        self.add_property("config_file", "configs/config.yml")
        
    def Birth(self):
        """Initialize the AB3DMOT tracker"""
        # Load configuration
        config_path = self.get_property("config_file")
        if os.path.exists(config_path):
            cfg = Config(config_path)
        else:
            # Use default parameters
            cfg = {
                'max_age': self.get_property("max_age"),
                'min_hits': self.get_property("min_hits"),
                'iou_threshold': self.get_property("iou_threshold")
            }
        
        # Initialize the authors' tracker
        self.tracker = AB3DMOT(cfg)
        self.frame_count = 0
        
    def Core(self):
        """Process one frame"""
        # Read detections from RTMaps input
        detections_data = self.input("detections_3d").read()
        timestamp = self.input("timestamp").read()
        
        # Convert RTMaps format to AB3DMOT format
        # Expected format: N x 7 (x, y, z, theta, l, w, h)
        detections = self.rtmaps_to_ab3dmot_format(detections_data)
        
        # Run the tracker update
        tracks = self.tracker.update(detections, self.frame_count)
        
        # Convert tracks back to RTMaps format
        if len(tracks) > 0:
            track_data, track_ids = self.ab3dmot_to_rtmaps_format(tracks)
            self.output("tracks_3d").write(track_data)
            self.output("track_ids").write(track_ids)
        
        self.frame_count += 1
        
    def rtmaps_to_ab3dmot_format(self, rtmaps_detections):
        """Convert RTMaps detection format to AB3DMOT format"""
        # Assuming RTMaps provides detections as structured array
        # Convert to numpy array with shape (N, 7)
        # Format: [x, y, z, theta, l, w, h] for each detection
        
        if hasattr(rtmaps_detections, 'data'):
            # If it's an RTMaps structure
            num_detections = len(rtmaps_detections.data) // 7
            detections = np.array(rtmaps_detections.data).reshape(num_detections, 7)
        else:
            # If it's already a numpy array
            detections = np.array(rtmaps_detections)
            
        return detections
        
    def ab3dmot_to_rtmaps_format(self, tracks):
        """Convert AB3DMOT tracks to RTMaps format"""
        track_data = []
        track_ids = []
        
        for track in tracks:
            # AB3DMOT track format: [x, y, z, theta, l, w, h, track_id]
            track_data.extend(track[:7])  # Position and dimensions
            track_ids.append(int(track[7]))  # Track ID
            
        return np.array(track_data, dtype=np.float32), np.array(track_ids, dtype=np.int32)
        
    def Death(self):
        """Cleanup"""
        del self.tracker