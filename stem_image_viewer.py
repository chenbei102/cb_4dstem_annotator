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
    QFileDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

import os
import numpy as np
import cv2



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
        self.load_btn.clicked.connect(self.load_data)

        layout = QGridLayout()
        layout.addWidget(self.load_btn, 0, 1)
        layout.addWidget(self.fname_display, 1, 0, 1, 3)
        layout.addWidget(self.image_label, 2, 0, 5, 3)
        layout.addWidget(self.coord_display, 7, 1)
        self.setLayout(layout)

        self.rect_select_mode = False
        

    def load_data(self):
        """
        Load the 4D STEM dataset from a NumPy `.npz` file and compute a 2D virtual
        STEM image from the 4D dataset. 
        """

        fpath, _ = QFileDialog.getOpenFileName(
            self, "Select a File", "",
            "NumPy Data (*.npz);;All Files (*)"
        )
        
        if fpath:
            self.fname_display.setText(f"File Name: {os.path.basename(fpath)}")
            self.work_dir = os.path.dirname(fpath)
        else:
            return

        data = np.load(fpath)
        var_name = data.files[0]
        data = data[var_name]
        
        ss = data.shape
        self.h_image, self.w_image = ss[:2]

        self.image = np.sum(data, axis=(2, 3))

        val_min = np.min(self.image)
        val_max = np.max(self.image)

        self.image = 255 * (self.image - val_min) / (val_max - val_min) 
        self.image = self.image.astype(np.uint8)

        img = cv2.cvtColor(self.image, cv2.COLOR_GRAY2RGB)

        q_img = QImage(img.data, self.w_image, self.h_image, 3*self.w_image,
                       QImage.Format.Format_RGB888) 

        self.pixmap_original = QPixmap().fromImage(q_img)

        self.image_label_size = self.image_label.size()

        self.pixmap = self.pixmap_original.scaled(self.image_label_size,
                                                  Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)

        self.image_label.setPixmap(self.pixmap)

        
    def keyPressEvent(self, event):
        """
        Handle key press events.
        Activate rectangular selection mode when the Shift key is pressed.
        """

        if event.key() == Qt.Key_Shift:
            self.rect_select_mode = True
        super().keyPressEvent(event)


    def keyReleaseEvent(self, event):
        """
        Handle key release events.
        Deactivate rectangular selection mode when the Shift key is released.
        """
        if event.key() == Qt.Key_Shift:
            self.rect_select_mode = False
        super().keyReleaseEvent(event)
        
