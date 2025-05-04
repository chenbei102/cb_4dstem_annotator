# -*- coding: utf-8 -*-

"""
stem_image_viewer.py

This module provides the `STEMImageViewer` class for interactive visualization of
a virtual STEM image which is a 2D representation derived from this 4D STEM
data, allowing for intuitive navigation of the spatial dimensions.

It allows users to interact with the displayed image to select specific spatial
scan points or define rectangular regions of interest.

Features:
- Load and display virtual STEM images computed from 4D STEM datasets.
- Click on the virtual STEM image to select a individual spatial scan point.
- Use click and Shift+click to select rectangular regions of scan points.

Author:
    Bei Chen

License:
    GPL-3.0 license
"""

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
)
from PyQt5.QtCore import Qt



class STEMImageViewer(QWidget):
    """
    An interactive viewer for visualizing 4D STEM data.

    This class provides a graphical interface to load 4D STEM data and display
    a 2D virtual STEM images computed from this data. It allows users to
    interact with the displayed image to select specific spatial scan points or
    define rectangular regions of interest.

    User Interaction:
        - Clicking on the image selects a single spatial scan point.
        - Clicking and holding Shift while clicking a second point defines
          a rectangular region of interest.
    """

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Interactive Virtual STEM Image Viewer")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(256, 256)
        
        self.fname_display = QLabel(f"File Name")
        self.fname_display.setAlignment(Qt.AlignCenter)

        self.coord_display = QLabel("Coordinates: (0, 0)")
        self.coord_display.setAlignment(Qt.AlignCenter)

        self.load_btn = QPushButton("Load Data")

        layout = QGridLayout()
        layout.addWidget(self.load_btn, 0, 1)
        layout.addWidget(self.fname_display, 1, 0, 1, 3)
        layout.addWidget(self.image_label, 2, 0, 5, 3)
        layout.addWidget(self.coord_display, 7, 1)
        self.setLayout(layout)
