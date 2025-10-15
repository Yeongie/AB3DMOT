# AB3DMOT Dependency Comparison & Version Notes

## Overview
This document compares the original AB3DMOT requirements with the working versions used in this project, documenting the "dependency hell" solutions that were implemented.

## Version Comparison

### Original AB3DMOT Requirements (from docs/INSTALL.md)
| Package | Original Version | Notes |
|---------|------------------|-------|
| scikit-learn | 0.19.2 | ✅ **KEPT SAME** |
| filterpy | 1.4.5 | ✅ **KEPT SAME** |
| numba | 0.43.1 | ✅ **KEPT SAME** |
| matplotlib | 2.2.3 | ✅ **KEPT SAME** |
| pillow | 6.2.2 | ⚠️ **CHANGED** |
| opencv-python | 4.2.0.32 | ✅ **KEPT SAME** |
| glob2 | 0.6 | ✅ **KEPT SAME** |
| PyYAML | 5.4 | ✅ **KEPT SAME** |
| easydict | 1.9 | ✅ **KEPT SAME** |
| llvmlite | 0.32.1 | ✅ **KEPT SAME** |
| wheel | 0.37.1 | ✅ **KEPT SAME** |

### Current Working Versions (from pip list)
| Package | Current Version | Status | Reason for Change |
|---------|-----------------|--------|-------------------|
| scikit-learn | 0.19.2 | ✅ **SAME** | No issues |
| filterpy | 1.4.5 | ✅ **SAME** | No issues |
| numba | 0.43.1 | ✅ **SAME** | No issues |
| matplotlib | 2.2.3 | ✅ **SAME** | No issues |
| Pillow | 8.4.0 | ⚠️ **UPGRADED** | **CRITICAL FIX** |
| opencv-python | 4.2.0.32 | ✅ **SAME** | No issues |
| glob2 | 0.6 | ✅ **SAME** | No issues |
| PyYAML | 5.4 | ✅ **SAME** | No issues |
| easydict | 1.9 | ✅ **SAME** | No issues |
| llvmlite | 0.32.1 | ✅ **SAME** | No issues |
| wheel | 0.37.1 | ✅ **SAME** | No issues |

### Additional Packages Added
| Package | Version | Purpose |
|---------|---------|---------|
| imageio | 2.15.0 | Video processing |
| scikit-video | 1.1.11 | Video encoding/decoding |
| scikit-image | 0.15.0 | Image processing |
| numpy | 1.19.5 | Array operations |
| scipy | 1.5.4 | Scientific computing |

## Critical Dependency Issues & Solutions

### 1. **Pillow Version Issue** ⚠️ **CRITICAL**
- **Original**: `pillow==6.2.2`
- **Working**: `pillow>=8.3.2` (currently 8.4.0)
- **Problem**: Pillow 6.2.2 has security vulnerabilities and compatibility issues with newer Python versions
- **Solution**: Upgraded to Pillow 8.4.0 for security and stability
- **Impact**: Required for image processing and visualization

### 2. **Video Processing Dependencies** 🆕 **ADDED**
- **Added**: `scikit-video`, `imageio`, `imageio-ffmpeg`
- **Problem**: Original AB3DMOT didn't include video processing dependencies
- **Solution**: Added these packages for visualization script functionality
- **Impact**: Enables video generation from tracking results

### 3. **FFmpeg Codec Issue** 🔧 **FIXED**
- **Problem**: Windows ffmpeg builds often lack `libx264` codec
- **Solution**: Modified `xinshuo_video/video_processing.py` to use `mpeg4` instead of `libx264`
- **Impact**: Prevents video generation failures on Windows

## Dependency Hell Solutions

### Issue 1: Pillow Security Vulnerabilities
```bash
# Original (vulnerable)
pillow==6.2.2

# Fixed (secure)
pillow>=8.3.2
```

### Issue 2: Missing Video Dependencies
```bash
# Added for visualization
pip install scikit-video imageio imageio-ffmpeg
```

### Issue 3: FFmpeg Codec Compatibility
```python
# Original (fails on Windows)
outputdict = {'-vcodec': 'libx264', ...}

# Fixed (works on Windows)
outputdict = {'-vcodec': 'mpeg4', ...}
```

## Installation Commands for New Team Member

### Step 1: Core Dependencies (from requirements.txt)
```bash
pip install -r requirements.txt
```

### Step 2: Additional Video Processing
```bash
pip install scikit-video imageio imageio-ffmpeg
```

### Step 3: Verify Installation
```bash
python -c "import AB3DMOT_libs; print('Core imports OK')"
python -c "from skvideo.io import FFmpegWriter; print('Video processing OK')"
ffmpeg -version
```

## Version Compatibility Matrix

| Python Version | Pillow | OpenCV | Status |
|----------------|--------|--------|--------|
| 3.6 | 6.2.2 | 4.2.0.32 | ❌ Vulnerable |
| 3.6 | 8.4.0 | 4.2.0.32 | ✅ Working |
| 3.8 | 8.4.0 | 4.2.0.32 | ✅ Tested |
| 3.9+ | 8.4.0 | 4.2.0.32 | ⚠️ Untested |

## Recommendations for Team Member

### ✅ **DO NOT CHANGE**
- Keep all core AB3DMOT dependencies at exact versions
- Maintain Pillow >= 8.3.2 for security
- Keep OpenCV 4.2.0.32 (newer versions may break compatibility)

### ⚠️ **BE CAREFUL WITH**
- NumPy version (currently 1.19.5) - newer versions may break numba
- Python version - stick to 3.6-3.8 for best compatibility
- FFmpeg builds - ensure mpeg4 codec is available

### 🆕 **CAN ADD**
- Additional visualization packages
- Development tools (pytest, black, etc.)
- Documentation tools (sphinx, etc.)

## Troubleshooting Common Issues

### Issue: "Pillow security vulnerability"
**Solution**: Upgrade to Pillow >= 8.3.2

### Issue: "FFmpeg codec not found"
**Solution**: Check `ffmpeg -encoders` and use mpeg4 instead of libx264

### Issue: "Import errors with numba"
**Solution**: Ensure NumPy version compatibility (1.19.5 works well)

### Issue: "Video generation fails"
**Solution**: Install scikit-video and imageio packages

---

**Key Takeaway**: The main change from original AB3DMOT is upgrading Pillow for security, adding video processing dependencies, and fixing FFmpeg codec compatibility. All core tracking dependencies remain at original versions for stability.
