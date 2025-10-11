# Changes Made to AB3DMOT

This document summarizes all modifications made to the original AB3DMOT repository.

## Summary of Changes

Based on the original [AB3DMOT repository](https://github.com/xinshuoweng/AB3DMOT), the following enhancements have been made:

### 🆕 New Features Added

1. **CSV Export Functionality**
   - Added `--export_csv` command line flag to `main.py`
   - Created `AB3DMOT_libs/csv_export.py` - Modular CSV export component
   - Generates CSV files with tracking results for each hypothesis
   - Includes comprehensive CSV export documentation (`CSV_EXPORT_GUIDE.md`)

2. **Enhanced Documentation**
   - `CSV_EXPORT_GUIDE.md` - Complete guide for CSV export feature
   - `example_output/` - Sample CSV output files

### 🔧 Bug Fixes & Improvements

1. **Calibration File Parsing Fix** (`AB3DMOT_libs/kitti_calib.py`)
   - Fixed parsing of KITTI calibration files with inconsistent format
   - Handles lines both with and without colons
   - Proper parameter name mapping (`R_rect` → `R0_rect`, etc.)

2. **Import Path Resolution** 
   - Fixed `ModuleNotFoundError` in scripts by adding proper `sys.path` handling:
     - `scripts/post_processing/trk_conf_threshold.py`
     - `scripts/KITTI/evaluate.py` 
     - `scripts/post_processing/visualization.py`

3. **Repository Structure**
   - Added comprehensive `.gitignore` to exclude large data files
   - Organized code into modular components

### 📁 New Files Created

- `AB3DMOT_libs/csv_export.py` - CSV export functionality
- `CSV_EXPORT_GUIDE.md` - Documentation for CSV export
- `example_output/*.csv` - Sample output files
- `.gitignore` - Git ignore rules for large files
- Helper files: `check_detections.py`, `dummy_detector.py`, `tracker_component.py`

### 🔄 Modified Files

1. **`main.py`**
   - Added `--export_csv` argument parser
   - Integrated CSV export functionality
   - Added CSV export initialization and cleanup

2. **`AB3DMOT_libs/kitti_calib.py`**
   - Enhanced `read_calib_file()` method for robust parsing
   - Added parameter name mapping for KITTI format variations

3. **Script Files** (Import path fixes)
   - `scripts/post_processing/trk_conf_threshold.py`
   - `scripts/KITTI/evaluate.py`
   - `scripts/post_processing/visualization.py`

## Usage

### Original AB3DMOT Usage
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn
```

### New CSV Export Usage
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv
```

