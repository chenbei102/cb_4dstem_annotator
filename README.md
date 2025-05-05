# cb_4dstem_annotator

This repository provides **an interactive annotation tool for 4D STEM (Scanning Transmission Electron Microscopy) data**. It is designed to faciliate the navigation, visualization, and annotation of complex 4D datasets. The tool would be useful for researchers and scientists in materials science, electron microscopy, and related fields where diffraction pattern analysis is required.

<div align="center">
  <img src="fig/screenshot1.png" alt="Figure 1" style="width: 95%;">
  <p><strong>Screenshots of the Virtual STEM Image Viewer and Diffraction Pattern Annotator <br />with a single scan point selected</strong></p>
</div>

<div align="center">
  <img src="fig/screenshot2.png" alt="Figure 1" style="width: 94%;">
  <p><strong>Screenshots of the Virtual STEM Image Viewer and Diffraction Pattern Annotator <br />with a rectangular region of scan points selected</strong></p>
</div>

## Getting Started

### Requirements

This code has been tested and works with the following dependencies:

- **Python** 3.12.4
- **NumPy** 2.1.0
- **OpenCV-Python** 4.11.0.86
- **PyQt5** 5.15.11
- **QtPy** 2.4.1

Ensure that all required packages are installed before running the code.

It's recommended to use a virtual environment to manage dependencies and avoid conflicts with other Python projects. For example, we can use `conda`:

```bash
conda create -n test_4dstem python=3.12
```

Once the environment is created, activate it:

```bash
conda activate test_4dstem
```

Next, use `pip` to install the required dependencies:

```bash
pip install numpy opencv-python PyQt5 QtPy
```
