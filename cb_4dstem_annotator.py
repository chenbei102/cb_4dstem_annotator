# -*- coding: utf-8 -*-

"""
cb_4dstem_annotator - Main Entry Point

This module contains the main function for `cb_4dstem_annotator`, an interactive 
annotation tool designed to support the exploration, visualization, and annotation 
of complex 4D STEM (Scanning Transmission Electron Microscopy) datasets.

4D STEM data comprise a 2D diffraction pattern at each point of a 2D spatial scan
of a sample. This tool allows users to interactively explore these datasets,
visualize and annotate diffraction patterns, and extract the coordinates of bright
spots for further analysis.

Usage:
    Run this module to launch the application:
    ```bash
    python cb_4dstem_annotator.py
    ```

Author:
    Bei Chen

License:
    GPL-3.0 license
"""

from stem_image_viewer import STEMImageViewer
from PyQt5.QtWidgets import QApplication

import sys



if __name__ == '__main__':

    app = QApplication(sys.argv)

    viewer = STEMImageViewer()
    viewer.resize(600, 600)
    viewer.move(50, 100)
    viewer.show()
    
    sys.exit(app.exec_())
