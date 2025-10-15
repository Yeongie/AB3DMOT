# AB3DMOT
To read the original official AB3DMOT README.md visit https://github.com/xinshuoweng/AB3DMOT/blob/master/README.md
Please also check HANDOVER_GUIDE.md and DEPENDANCY_COMPARISON.md

Note: You need to visit https://www.cvlibs.net/datasets/kitti/eval_tracking.php and download the following datasets:
data_tracking_calib.zip
data_tracking_image_2.zip
data_tracking_label_2.zip
data_tracking_oxts.zip
data_tracking_velodyne.zip

directory path will end up looking like this:
data/KITTI/tracking/
├── training/
│   ├── image_02/    # 0000/, 0001/, 0002/, ..., 0020/
│   ├── velodyne/    # LiDAR point clouds
│   ├── calib/       # Camera calibration
│   ├── label_02/    # Ground truth labels
│   └── oxts/        # GPS/IMU data
└── testing/
    ├── image_02/    # Testing sequences
    ├── velodyne/    # LiDAR point clouds
    ├── calib/       # Camera calibration
    └── oxts/        # GPS/IMU data

## Installation

Please follow carefully our provided [installation instructions](docs/INSTALL.md), to avoid errors when running the code.

#### Prerequisites
- Windows 10/11 (current setup tested on Windows 10)
- Python 3.6+ (tested with Python 3.8)
- Git
- RTMaps (if continuing RTMaps integration work)

#### Environment Setup

1. **Clone and Navigate to Project**
   ```bash
   git clone <repository-url>
   cd AB3DMOT
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Additional Dependencies for Video Processing**
   ```bash
   pip install scikit-video imageio imageio-ffmpeg
   ```

5. **Verify FFmpeg Installation**
   ```bash
   ffmpeg -version
   ```
   - If not installed, download from https://ffmpeg.org/download.html
   - Add to system PATH

#### Current Project Status

**✅ Completed:**
- AB3DMOT core tracking algorithm working
- RTMaps integration component (`rtmaps_ab3dmot_tracker.py`) functional
- Video visualization fixed (codec compatibility issue resolved)
- Basic tracking pipeline operational

**⚠️ Known Issues:**
- RTMaps component uses simplified tracking fallback for stability

**🔄 Next Steps:**
1. Re-download KITTI/nuScenes datasets
2. Test full AB3DMOT pipeline with real data
3. Optimize RTMaps integration 
4. Connect real sensor inputs to RTMaps component

#### RTMaps Integration Files
- `rtmaps_components/` - RTMaps Python components
- `RTMAPS_INTEGRATION.md` - Detailed RTMaps setup guide
- `CHANGES_SUMMARY.md` - Complete change log

#### Quick Test
```bash
# Test basic functionality (requires data)
python main.py --dataset KITTI --split val --det_name pointrcnn

# Test visualization (after running tracking)
python scripts/post_processing/visualization.py --result_sha pointrcnn_val_H1_thres --split val
```

## Quick Demo on KITTI

To quickly get a sense of our method's performance on the KITTI dataset, one can run the following command after installation of the code. This step does not require you to download any dataset (a small set of data is already included in this code repository).

### Complete AB3DMOT Pipeline Commands

#### 1. Run Tracking (Choose one based on your needs)

**For validation set:**
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn
```

**For test set:**
```bash
python main.py --dataset KITTI --split test --det_name pointrcnn
```

**With CSV export:**
```bash
python main.py --dataset KITTI --split val --det_name pointrcnn --export_csv
```

#### 2. Apply Confidence Thresholding (validity of this is still in the air)
```bash
python scripts/post_processing/trk_conf_threshold.py --dataset KITTI --result_sha pointrcnn_val_H1
```

#### 3. Generate Visualization
```bash
# Create visualization images and videos
python scripts/post_processing/visualization.py --result_sha pointrcnn_val_H1_thres --split val
```

**Note**: The visualization script will create both individual frame images and MP4 videos. If video generation fails due to ffmpeg codec issues, the images will still be created successfully.

### Alternative Video Generation Options

#### Direct Video Processing Functions
```python
# Programmatic video generation
from xinshuo_video import generate_video_from_folder
generate_video_from_folder(image_folder, output_video, framerate=30)
```

### Note on video generation codecs (Windows/ffmpeg)

The visualization script writes videos via ffmpeg. On some Windows builds, ffmpeg is compiled without `libx264`, which caused failures when encoding with `-vcodec libx264`. To improve compatibility, the default codec in `xinshuo_video/video_processing.py` has been switched to `mpeg4`.

- If you have an ffmpeg build with x264 and prefer H.264, you can change `'-vcodec': 'mpeg4'` back to `'-vcodec': 'libx264'` in `xinshuo_video/video_processing.py`.
- To check codec availability: run `ffmpeg -hide_banner -encoders | findstr /I 264`.


