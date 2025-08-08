import pickle

# This is the path to the pre-computed detections for the first sequence
detection_file_path = 'data/KITTI/detection/pointrcnn_Car_val/data/0001.txt'

try:
    with open(detection_file_path, 'rb') as f:
        detections = pickle.load(f)

    if not detections:
        print("RESULT: The detection file is empty or has no data.")
    else:
        num_frames_with_detections = len(detections)
        print(f"RESULT: Successfully loaded the detection file.")
        print(f"Found detections for {num_frames_with_detections} frames.")

        total_dets = 0
        for frame_id in detections:
            if 'name' in detections[frame_id]:
                total_dets += len(detections[frame_id]['name'])
        print(f"Total number of detections in the file: {total_dets}")


except FileNotFoundError:
    print(f"ERROR: Detection file not found at '{detection_file_path}'")
except Exception as e:
    print(f"An error occurred: {e}")