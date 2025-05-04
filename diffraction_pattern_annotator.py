# -*- coding: utf-8 -*-

"""
diffraction_pattern_annotator.py

This module provides an interactive tool for annotating diffraction pattern images.

It defines the `DPsAnnotator` class that enables users to:
- Load and display diffraction patterns corresponding to different scan points of a sample.
- Navigate through diffraction patterns interactively.
- Annotate bright spots on the images.
- Export the coordinates of annotated spots to a text file for further analysis.

Author:
    Bei Chen

License:
    GPL-3.0 license
"""

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QSpinBox,
    QCheckBox,
    QListWidget,
    QAbstractItemView,
    QPushButton,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

import cv2



class DPsAnnotator(QWidget):
    """
    An interactive tool for annotating diffraction pattern images.

    This class provides a graphical user interface for displaying diffraction
    pattern images from 4D STEM data. It supports navigation through datasets,
    manual annotation of bright spots, and exporting of annotated coordinates.

    User Interaction:
        - Click on the image to annotate bright spots with circular markers.
        - Hold Shift to activate selection mode.
    """

    def __init__(self, data=None, work_dir='.', viewer=None):

        super().__init__()

        self.setWindowTitle("Interactive Diffraction Pattern Annotator")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(256, 256)

        self.fname_display = QLabel(f"Image Index: (0, 0)")
        self.fname_display.setAlignment(Qt.AlignCenter)

        self.coord_display = QLabel("Coordinates: (0, 0)")
        self.coord_display.setAlignment(Qt.AlignCenter)

        self.spot_size_spin = QSpinBox()
        self.spot_size_spin.setRange(1, 100)

        self.spot_display = QCheckBox("Show Spots")
        self.spot_display.setChecked(True) 

        self.select_chkbox = QCheckBox("Select Mode")
        self.select_chkbox.setChecked(False) 

        self.coord_list = QListWidget()
        self.coord_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.del_btn = QPushButton("Delete Selected")

        self.prev_btn = QPushButton("Previous Image")

        self.export_btn = QPushButton("Export Data")

        self.next_btn = QPushButton("Next Image")

        main_layout = QGridLayout()

        wl = 9
        wr = 3
        h1 = 5
        
        main_layout.addWidget(self.fname_display, 0, 0, 1, wl)
        main_layout.addWidget(self.image_label, 1, 0, h1+1, wl)
        main_layout.addWidget(self.coord_display, h1+2, wl // 2)

        main_layout.addWidget(self.spot_display, 1, wl, 1, 1)
        main_layout.addWidget(self.select_chkbox, 1, wl+wr-1, 1, 1)
        main_layout.addWidget(QLabel("Spot Size:"), 0, wl, 1, 1)
        main_layout.addWidget(self.spot_size_spin, 0, wl+1, 1, wr-1)

        main_layout.addWidget(self.coord_list, 2, wl, h1-1, wr)
        main_layout.addWidget(self.del_btn, h1+1, wl, 1, wr)
        main_layout.addWidget(self.prev_btn, h1+2, wl, 1, 1)
        main_layout.addWidget(self.export_btn, h1+2, wl+1, 1, 1)
        main_layout.addWidget(self.next_btn, h1+2, wl+2, 1, 1)

        self.setLayout(main_layout)

        self.work_dir = work_dir
        self.viewer_window = viewer

        self.image_index = 0

        self.pixmap = None
        self.pixmap_original = None
        
        if data is not None:
            self.num_row, self.num_col, self.h_image, self.w_image = data.shape
            self.num_images = self.num_row * self.num_col 

            self.images = data
            self.load_image(self.image_index)

            
    def load_image(self, index):
        """
        Load a diffraction pattern from a 4D STEM dataset using a 1D index,
        and display the corresponding diffraction pattern image.
        """

        self.image_index = index

        xx = self.image_index % self.num_col
        yy = self.image_index // self.num_col

        self.fname_display.setText(f"Image Index: ({xx:d}, {yy:d})")

        img = cv2.cvtColor(self.images[yy, xx, ...], cv2.COLOR_GRAY2RGB)

        q_img = QImage(img.data, self.w_image, self.h_image, 3*self.w_image,
                       QImage.Format.Format_RGB888) 

        self.pixmap_original = QPixmap().fromImage(q_img)

        self.image_label_size = self.image_label.size()
        self.pixmap = self.pixmap_original.scaled(self.image_label_size,
                                                  Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)

        self.image_label.setPixmap(self.pixmap)
