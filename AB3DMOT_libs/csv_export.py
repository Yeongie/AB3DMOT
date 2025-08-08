# Author: Modified for AB3DMOT CSV Export
# CSV Export Module for AB3DMOT Tracking Results

import os
import csv
from typing import Dict, TextIO, Any

class CSVExporter:
    """
    Dedicated class for exporting AB3DMOT tracking results to CSV format.
    Keeps CSV functionality organized and separate from core tracking logic.
    """
    
    def __init__(self, save_dir: str, num_hypo: int = 1):
        """
        Initialize CSV exporter
        
        Args:
            save_dir: Directory to save CSV files
            num_hypo: Number of hypotheses to track
        """
        self.save_dir = save_dir
        self.num_hypo = num_hypo
        self.csv_files: Dict[int, TextIO] = {}
        self.csv_writers: Dict[int, csv.writer] = {}
        
    def get_csv_header(self) -> list:
        """
        Define CSV column headers for tracking results
        
        Returns:
            List of column names for CSV header
        """
        return [
            'frame',           # Frame number in sequence
            'track_id',        # Unique tracking ID
            'object_type',     # Car, Pedestrian, Cyclist
            'truncated',       # Object truncation flag (0/1)
            'occluded',        # Object occlusion level (0-3)
            'alpha',           # Observation angle of object
            'bbox_left',       # 2D bounding box left coordinate
            'bbox_top',        # 2D bounding box top coordinate  
            'bbox_right',      # 2D bounding box right coordinate
            'bbox_bottom',     # 2D bounding box bottom coordinate
            'height_3d',       # 3D object height (meters)
            'width_3d',        # 3D object width (meters)
            'length_3d',       # 3D object length (meters)
            'x_3d',            # 3D position X in camera coordinates
            'y_3d',            # 3D position Y in camera coordinates
            'z_3d',            # 3D position Z in camera coordinates
            'rotation_y',      # 3D rotation around Y-axis (radians)
            'confidence_score' # Detection/tracking confidence (0.0-1.0)
        ]
    
    def init_sequence_files(self, seq_name: str) -> None:
        """
        Initialize CSV files for a new sequence
        
        Args:
            seq_name: Name of the sequence (e.g., '0001')
        """
        # Close any existing files first
        self.close_files()
        
        # Create new CSV files for each hypothesis
        for hypo in range(self.num_hypo):
            csv_filename = f'tracking_results_H{hypo}_{seq_name}.csv'
            csv_path = os.path.join(self.save_dir, csv_filename)
            
            # Open file with proper encoding
            csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
            csv_writer = csv.writer(csv_file)
            
            # Write header row
            csv_writer.writerow(self.get_csv_header())
            
            # Store file handles and writers
            self.csv_files[hypo] = csv_file
            self.csv_writers[hypo] = csv_writer
    
    def export_result(self, result_data: Any, hypo: int, det_id2str: Dict, 
                     frame: int, score_threshold: float) -> None:
        """
        Export a single tracking result to CSV
        
        Args:
            result_data: Tracking result array (N x 15 format)
            hypo: Hypothesis index
            det_id2str: Detection ID to string mapping
            frame: Current frame number
            score_threshold: Minimum confidence threshold
        """
        if hypo not in self.csv_writers:
            return  # Skip if hypothesis not initialized
            
        # Extract data from result array
        # Format: [h, w, l, x, y, z, theta, id, ori, type_id, bbox2d(4), conf]
        bbox3d_tmp = result_data[0:7]     # [height, width, length, x, y, z, rotation]
        id_tmp = result_data[7]           # Track ID
        ori_tmp = result_data[8]          # Observation angle (alpha)  
        type_tmp = det_id2str[result_data[9]]  # Object type string
        bbox2d_tmp = result_data[10:14]   # 2D bounding box [left, top, right, bottom]
        conf_tmp = result_data[14]        # Confidence score
        
        # Only export results above confidence threshold
        if conf_tmp >= score_threshold:
            csv_row = [
                frame,                    # frame
                int(id_tmp),             # track_id  
                type_tmp,                # object_type
                0,                       # truncated (placeholder)
                0,                       # occluded (placeholder)
                ori_tmp,                 # alpha
                bbox2d_tmp[0],           # bbox_left
                bbox2d_tmp[1],           # bbox_top
                bbox2d_tmp[2],           # bbox_right
                bbox2d_tmp[3],           # bbox_bottom
                bbox3d_tmp[0],           # height_3d
                bbox3d_tmp[1],           # width_3d
                bbox3d_tmp[2],           # length_3d
                bbox3d_tmp[3],           # x_3d
                bbox3d_tmp[4],           # y_3d
                bbox3d_tmp[5],           # z_3d
                bbox3d_tmp[6],           # rotation_y
                conf_tmp                 # confidence_score
            ]
            
            self.csv_writers[hypo].writerow(csv_row)
    
    def close_files(self) -> None:
        """Close all open CSV files"""
        for csv_file in self.csv_files.values():
            if csv_file and not csv_file.closed:
                csv_file.close()
        
        self.csv_files.clear()
        self.csv_writers.clear()
    
    def get_export_summary(self, seq_name: str) -> str:
        """
        Get summary of exported CSV files
        
        Args:
            seq_name: Sequence name
            
        Returns:
            Summary string of exported files
        """
        summary_lines = [f"CSV Export Summary for Sequence {seq_name}:"]
        
        for hypo in range(self.num_hypo):
            csv_filename = f'tracking_results_H{hypo}_{seq_name}.csv'
            csv_path = os.path.join(self.save_dir, csv_filename)
            
            if os.path.exists(csv_path):
                file_size = os.path.getsize(csv_path) / 1024  # KB
                with open(csv_path, 'r') as f:
                    line_count = sum(1 for _ in f) - 1  # Subtract header
                
                summary_lines.append(
                    f"  H{hypo}: {csv_filename} ({line_count} records, {file_size:.1f} KB)"
                )
        
        return "\n".join(summary_lines)


# Convenience functions for backward compatibility and easier integration
def create_csv_exporter(save_dir: str, num_hypo: int = 1) -> CSVExporter:
    """
    Factory function to create a CSV exporter instance
    
    Args:
        save_dir: Directory to save CSV files
        num_hypo: Number of hypotheses
        
    Returns:
        Configured CSVExporter instance
    """
    return CSVExporter(save_dir, num_hypo)


def export_tracking_results_csv(save_dir: str, seq_name: str, results_data: list,
                               det_id2str: Dict, frame: int, score_threshold: float,
                               num_hypo: int = 1) -> None:
    """
    Standalone function to export tracking results to CSV
    
    Args:
        save_dir: Directory to save CSV files
        seq_name: Sequence name
        results_data: List of tracking results for each hypothesis
        det_id2str: Detection ID to string mapping
        frame: Current frame number
        score_threshold: Minimum confidence threshold
        num_hypo: Number of hypotheses
    """
    exporter = CSVExporter(save_dir, num_hypo)
    exporter.init_sequence_files(seq_name)
    
    for hypo in range(num_hypo):
        if hypo < len(results_data):
            for result in results_data[hypo]:
                exporter.export_result(result, hypo, det_id2str, frame, score_threshold)
    
    exporter.close_files()