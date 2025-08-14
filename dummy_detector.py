import sys
# Add the RTMaps packages path to the system path
sys.path.append('C:/Program Files/Intempora/RTMaps 4/packages/rtmaps_python_bridge')

import rtmaps.types
from rtmaps.base_component import BaseComponent
import numpy as np
import pickle
import time

class rtmaps_python(BaseComponent):
    def __init__(self):
        BaseComponent.__init__(self)

    def Dynamic(self):
        # Define the outputs to match the tracker's inputs
        self.add_output("detections_3d", rtmaps.types.ANY)
        self.add_output("timestamp", rtmaps.types.ANY)

    def Birth(self):
        print("Dummy Detector Starting.")

    def Core(self):
        # Create a fake detection: [x, y, z, theta, l, w, h]
        fake_detection = np.array([10.0, 0.0, 0.0, 1.57, 4.5, 2.0, 1.8], dtype=np.float32)
        
        # Get a fake timestamp
        fake_timestamp = time.time()

        # Write the pickled data to the output ports
        self.outputs["detections_3d"].write(pickle.dumps(fake_detection))
        self.outputs["timestamp"].write(pickle.dumps(fake_timestamp))

        time.sleep(0.1)