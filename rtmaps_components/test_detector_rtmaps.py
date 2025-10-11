"""
Test detector component for RTMaps - generates fake car detections
Connect this to AB3DMOT tracker to see it work!
"""

import rtmaps.types
import rtmaps.core
import numpy as np
from rtmaps.base_component import BaseComponent

class rtmaps_python(BaseComponent):
    def __init__(self):
        BaseComponent.__init__(self)
        self.frame = 0
    
    def Dynamic(self):
        # Output: detection data
        self.add_output("detections", rtmaps.types.AUTO)
        
        # Properties
        self.add_property("num_cars", 2)
        self.add_property("frame_rate_ms", 100)
    
    def Birth(self):
        self.frame = 0
        num_cars = int(self.get_property("num_cars"))
        rtmaps.core.report_info(f"[Test Detector] Starting - will generate {num_cars} cars per frame")
    
    def Core(self):
        num_cars = int(self.get_property("num_cars"))
        frame_rate = int(self.get_property("frame_rate_ms"))
        
        # Generate moving car detections
        # Format: [h, w, l, x, y, z, theta, score]
        dets = []
        for i in range(num_cars):
            det = [
                1.5,                          # h - height
                1.8,                          # w - width  
                4.5,                          # l - length
                10.0 + i*5 + self.frame*0.5,  # x - moving forward
                i*2.0,                        # y - lateral position
                30.0 + i*5,                   # z - depth
                0.1,                          # theta - rotation
                0.9 + i*0.05                  # score - confidence
            ]
            dets.append(det)
        
        dets = np.array(dets, dtype=np.float64)
        
        # Ensure contiguous array (important for RTMaps!)
        dets = np.ascontiguousarray(dets.reshape(num_cars, 8))
        
        # Send to output
        output = rtmaps.types.Ioelt()
        output.data = dets
        self.outputs["detections"].write(output)
        
        rtmaps.core.report_info(f"[Test Detector] Frame {self.frame}: Sent {len(dets)} detections")
        
        self.frame += 1
        self.wait(frame_rate * 1000)  # Convert ms to microseconds


