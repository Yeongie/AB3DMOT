"""
Simple RTMaps component to log tracking results for testing
"""

import rtmaps
import rtmaps.types
import rtmaps.base_component
import numpy as np
import os
import time

class SimpleTrackerLogger(rtmaps.base_component.RTMapsBaseComponent):
    def __init__(self):
        rtmaps.base_component.RTMapsBaseComponent.__init__(self)
        
    def Dynamic(self):
        # Add input for tracking results
        self.add_input("tracks", rtmaps.types.ANY)
        
        # Add properties
        self.add_property("log_file", "tracking_results.txt")
        self.add_property("log_interval", 10)  # Log every N frames
        
    def Birth(self):
        rtmaps.core.report_info("[TrackerLogger] Birth() called")
        
        # Initialize logging
        self.frame_count = 0
        self.log_file = self.get_property("log_file")
        self.log_interval = int(self.get_property("log_interval"))
        
        # Create log file with header
        with open(self.log_file, 'w') as f:
            f.write("Frame,Timestamp,TrackID,X,Y,Z,Width,Height,Length,Rotation,Confidence\n")
        
        rtmaps.core.report_info(f"[TrackerLogger] Logging to: {self.log_file}")
        
    def Core(self):
        # Read tracking results
        tracks_input = self.inputs["tracks"].ioelt
        if tracks_input is None:
            return
            
        timestamp = tracks_input.ts
        tracks_data = tracks_input.data
        
        self.frame_count += 1
        
        # Log every N frames
        if self.frame_count % self.log_interval == 0:
            if len(tracks_data) > 0:
                rtmaps.core.report_info(f"[TrackerLogger] Frame {self.frame_count}: {len(tracks_data)} tracks received")
                
                # Log to file
                with open(self.log_file, 'a') as f:
                    for track in tracks_data:
                        track_id = int(track[0])
                        x, y, z = track[1], track[2], track[3]
                        w, h, l = track[4], track[5], track[6]
                        rotation = track[7]
                        confidence = track[14] if len(track) > 14 else 0.0
                        
                        f.write(f"{self.frame_count},{timestamp},{track_id},{x:.3f},{y:.3f},{z:.3f},{w:.3f},{h:.3f},{l:.3f},{rotation:.3f},{confidence:.3f}\n")
                        
                        # Also log to console
                        rtmaps.core.report_info(f"[TrackerLogger] Track {track_id}: pos=({x:.2f},{y:.2f},{z:.2f}) conf={confidence:.3f}")
            else:
                rtmaps.core.report_info(f"[TrackerLogger] Frame {self.frame_count}: No tracks received")
                
    def Death(self):
        rtmaps.core.report_info(f"[TrackerLogger] Death() called - logged {self.frame_count} frames to {self.log_file}")
