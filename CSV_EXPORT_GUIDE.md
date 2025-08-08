# AB3DMOT CSV Export Guide

## Overview
This guide explains how to export AB3DMOT tracking results to CSV format for easy analysis in Excel, Python pandas, or other data analysis tools.

## CSV Export Features

### ✅ **What's Included in CSV Export:**
- **Frame number** - Video frame index
- **Track ID** - Unique identifier for each tracked object
- **Object type** - Car, Pedestrian, or Cyclist
- **2D Bounding box** - Image coordinates (left, top, right, bottom)
- **3D Bounding box** - Real-world coordinates (height, width, length, x, y, z, rotation)
- **Confidence score** - Detection confidence (0.0 to 1.0)
- **Observation angle** - Viewing angle from camera

### 📊 **CSV Column Structure:**
```
frame, track_id, object_type, truncated, occluded, alpha,
bbox_left, bbox_top, bbox_right, bbox_bottom,
height_3d, width_3d, length_3d, x_3d, y_3d, z_3d, rotation_y,
confidence_score
```

## Usage Instructions

### **Basic Usage:**
```bash
# Enable CSV export with --export_csv flag
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv
```

### **Complete Workflow with CSV Export:**
```bash
# 1. Activate environment
conda activate ab3dmot

# 2. Navigate to project
cd C:\Users\sardo\Documents\EcoCAR\AB3DMOT

# 3. Run tracking with CSV export
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv

# 4. Apply confidence thresholding
python scripts/post_processing/trk_conf_threshold.py --dataset KITTI --result_sha pointrcnn_val_H1

# 5. Evaluate performance
python scripts/KITTI/evaluate.py pointrcnn_val_H1_thres 1 3D
```

## Output Files

### **CSV Files Location:**
```
results/KITTI/pointrcnn_val_H1/
├── tracking_results_H0_0000.csv    # Sequence 0000 results
├── tracking_results_H0_0001.csv    # Sequence 0001 results  
├── tracking_results_H0_0002.csv    # Sequence 0002 results
└── ...                             # One CSV per sequence
```

### **CSV File Naming Convention:**
- `tracking_results_H{hypothesis}_{sequence}.csv`
- `H0` = Hypothesis 0 (usually the main result)
- Sequence names match KITTI format (0000, 0001, etc.)

## Example CSV Content

```csv
frame,track_id,object_type,truncated,occluded,alpha,bbox_left,bbox_top,bbox_right,bbox_bottom,height_3d,width_3d,length_3d,x_3d,y_3d,z_3d,rotation_y,confidence_score
0,1,Car,0,0,-1.57,100.5,150.2,300.8,250.6,1.6,1.8,4.2,10.5,-1.2,45.3,0.1,0.95
0,2,Pedestrian,0,0,0.2,450.1,180.5,480.3,320.1,1.7,0.6,0.8,5.2,-1.8,12.1,-0.3,0.87
1,1,Car,0,0,-1.55,102.1,149.8,302.3,251.2,1.6,1.8,4.2,10.8,-1.2,46.1,0.12,0.94
```

## Data Analysis Examples

### **Python pandas Analysis:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
df = pd.read_csv('results/KITTI/pointrcnn_val_H1/tracking_results_H0_0001.csv')

# Basic statistics
print("Object types:", df['object_type'].value_counts())
print("Average confidence:", df['confidence_score'].mean())

# Track length analysis
track_lengths = df.groupby('track_id').size()
print("Average track length:", track_lengths.mean())

# Plot confidence distribution
df['confidence_score'].hist(bins=20)
plt.title('Confidence Score Distribution')
plt.show()
```

### **Excel Analysis:**
1. Open CSV file in Excel
2. Use Pivot Tables to analyze:
   - Object counts by type
   - Tracking duration per object
   - Confidence score statistics
3. Create charts for visualization

## Advanced Features

### **Multiple Hypotheses:**
If using multiple hypotheses (--num_hypo > 1), separate CSV files are created:
- `tracking_results_H0_{sequence}.csv` - Best hypothesis
- `tracking_results_H1_{sequence}.csv` - Alternative hypothesis

### **Filtering by Confidence:**
CSV export respects the confidence threshold setting:
```bash
# Only export tracks with confidence > 0.7
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv --score_threshold 0.7
```

### **Different Object Categories:**
```bash
# Export only car tracking results
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv --cat Car

# Export all categories (default)
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv
```

## Troubleshooting

### **Common Issues:**

1. **No CSV files generated:**
   - Ensure `--export_csv` flag is used
   - Check that tracking completed successfully
   - Verify results directory exists

2. **Empty CSV files:**
   - Check confidence threshold settings
   - Verify detection files contain valid data
   - Ensure proper dataset format

3. **CSV encoding issues:**
   - CSV files use UTF-8 encoding
   - Open with proper encoding in Excel or text editor

### **Performance Notes:**
- CSV export adds minimal overhead (~5% slower)
- CSV files are typically 10-20% larger than original text format
- Each sequence gets its own CSV file for easier analysis

## Integration with Other Tools

### **MATLAB:**
```matlab
% Load CSV data in MATLAB
data = readtable('tracking_results_H0_0001.csv');
disp(data(1:10, :));  % Show first 10 rows
```

### **R:**
```r
# Load CSV data in R
data <- read.csv('tracking_results_H0_0001.csv')
summary(data)
```

This CSV export feature makes AB3DMOT results easily accessible for research, analysis, and integration with other tools!