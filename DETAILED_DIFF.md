# Detailed Diff: AB3DMOT Modifications

Since GitHub cannot automatically compare the repositories, here is a detailed breakdown of all changes made to the original AB3DMOT repository.

## Files Added (New Files)

### Core Functionality
- `AB3DMOT_libs/csv_export.py` - **NEW**: Modular CSV export functionality
- `CSV_EXPORT_GUIDE.md` - **NEW**: Documentation for CSV export feature
- `CHANGES_SUMMARY.md` - **NEW**: This summary document

### Example Output
- `example_output/tracking_results_H0_example_seq.csv` - **NEW**: Sample CSV output
- `example_output/tracking_results_H0_multi_hypo_seq.csv` - **NEW**: Sample multi-hypothesis output
- `example_output/tracking_results_H0_standalone_example.csv` - **NEW**: Standalone example
- `example_output/tracking_results_H1_multi_hypo_seq.csv` - **NEW**: H1 hypothesis output
- `example_output/tracking_results_H1_standalone_example.csv` - **NEW**: H1 standalone example
- `example_output/tracking_results_H2_multi_hypo_seq.csv` - **NEW**: H2 hypothesis output

### Repository Management
- `.gitignore` - **NEW**: Comprehensive gitignore to exclude large files

### Helper Files
- `check_detections.py` - **NEW**: Detection verification utility
- `dummy_detector.py` - **NEW**: Testing utility
- `tracker_component.py` - **NEW**: Component isolation helper

## Files Modified (Existing Files Changed)

### Main Application
**`main.py`** - **MODIFIED**
- Added `--export_csv` command line argument
- Integrated CSV export functionality
- Added CSV exporter initialization and cleanup
- Added import for `CSVExporter` from `AB3DMOT_libs.csv_export`

### Core Libraries
**`AB3DMOT_libs/kitti_calib.py`** - **MODIFIED**
- Enhanced `read_calib_file()` method for robust parsing
- Added support for lines both with and without colons
- Added parameter name mapping: `R_rect` → `R0_rect`, `Tr_velo_cam` → `Tr_velo_to_cam`, `Tr_imu_velo` → `Tr_imu_to_velo`

### Script Files (Import Path Fixes)
**`scripts/post_processing/trk_conf_threshold.py`** - **MODIFIED**
- Added sys.path manipulation to resolve import issues
- Added: `sys.path.insert(0, root_dir)` where `root_dir = os.path.join(current_dir, '../../')`

**`scripts/KITTI/evaluate.py`** - **MODIFIED** 
- Added sys.path manipulation to resolve import issues
- Added: `sys.path.insert(0, root_dir)` where `root_dir = os.path.join(current_dir, '../../')`

**`scripts/post_processing/visualization.py`** - **MODIFIED**
- Added sys.path manipulation to resolve import issues  
- Added: `sys.path.insert(0, root_dir)` where `root_dir = os.path.join(current_dir, '../../')`

## Key Code Changes

### 1. CSV Export Integration in main.py

**Added argument parser:**
```python
parser.add_argument('--export_csv', action='store_true', help='Export tracking results to CSV format')
```

**Added CSV export logic:**
```python
# Initialize CSV exporter if enabled
csv_exporter = None
if cfg.export_csv:
    csv_exporter = CSVExporter(save_dir, cfg.num_hypo)
    csv_exporter.init_sequence_files(seq_name)

# In tracking loop - export results
if csv_exporter:
    csv_exporter.export_result(result_tmp, hypo, det_id2str, frame, cfg.score_threshold)

# Cleanup
if csv_exporter:
    csv_exporter.close_files()
    print_log(csv_exporter.get_export_summary(seq_name), log=log)
```

### 2. Calibration Fix in AB3DMOT_libs/kitti_calib.py

**Enhanced read_calib_file method:**
```python
def read_calib_file(self, filepath):
    data = {}
    param_mapping = {
        'R_rect': 'R0_rect',
        'Tr_velo_cam': 'Tr_velo_to_cam', 
        'Tr_imu_velo': 'Tr_imu_to_velo'
    }
    
    with open(filepath, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            if len(line)==0: continue
            
            # Handle both formats: "key: value" and "key value"
            if ':' in line:
                key, value = line.split(':', 1)
            else:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    key, value = parts
                else:
                    continue
                    
            # Map parameter names
            if key in param_mapping:
                key = param_mapping[key]
                
            try:
                data[key] = np.array([float(x) for x in value.split()])
            except ValueError:
                pass
    return data
```

### 3. Import Path Fixes

**Added to multiple script files:**
```python
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '../../')
sys.path.insert(0, root_dir)
```

## Usage Changes

### Original Usage:
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn
```

### New Usage with CSV Export:
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv
```

## Files Unchanged

All other files in the repository remain exactly as they were in the original AB3DMOT repository, including:
- All files in `xinshuo_*` directories (visualization, math, io, etc.)
- Configuration files in `configs/`
- Documentation in `docs/`
- All other library files in `AB3DMOT_libs/` not mentioned above

## Summary

- **6 new files** added for CSV functionality and documentation
- **5 existing files** modified for CSV integration, bug fixes, and import resolution
- **No files deleted** from the original repository
- All changes are additive and backward-compatible with the original functionality
