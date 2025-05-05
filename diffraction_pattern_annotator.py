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
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen

import cv2
import numpy as np



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
        self.image_label.setMouseTracking(True)
        self.image_label.mouseMoveEvent = self.move_cursor
        self.image_label.mousePressEvent = self.on_click

        self.fname_display = QLabel(f"Image Index: (0, 0)")
        self.fname_display.setAlignment(Qt.AlignCenter)

        self.coord_display = QLabel("Coordinates: (0, 0)")
        self.coord_display.setAlignment(Qt.AlignCenter)

        self.spot_size_spin = QSpinBox()
        self.spot_size_spin.setRange(1, 100)
        self.spot_size_spin.valueChanged.connect(self.update_spot_size)

        self.spot_display = QCheckBox("Show Spots")
        self.spot_display.setChecked(True) 
        self.spot_display.stateChanged.connect(self.toggle_spots)

        self.select_chkbox = QCheckBox("Select Mode")
        self.select_chkbox.setChecked(False) 
        self.select_chkbox.stateChanged.connect(self.toggle_select_mode)

        self.coord_list = QListWidget()
        self.coord_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.coord_list.itemSelectionChanged.connect(self.highlight_spots)

        self.del_btn = QPushButton("Delete Selected")
        self.del_btn.clicked.connect(self.delete_selected)

        self.prev_btn = QPushButton("Previous Image")
        self.prev_btn.clicked.connect(self.load_prev_image)

        self.export_btn = QPushButton("Export Data")

        self.next_btn = QPushButton("Next Image")
        self.next_btn.clicked.connect(self.load_next_image)

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

        self.cursor_pos = None
        self.pixmap = None
        self.pixmap_original = None
        
        self.spot_size = 20
        self.spot_size_spin.setValue(self.spot_size)

        self.spots = []
        self.spot_coords = []

        self.select_mode = False
        self.show_spots = True
        
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

        self.update_display()


    def combine_images(self, low_bound, up_bound):
        """
        Combine diffraction pattern images for all scan points within a
        rectangular region specified by `low_bound` and `up_bound`.
        """

        x1, y1 = low_bound
        x2, y2 = up_bound
        x2 += 1
        y2 += 1

        self.index_range = (x1, x2, y1, y2)

        self.fname_display.setText(f"Image Index Range: ({x1:d}:{x2:d}, {y1:d}:{y2:d})")

        image = np.sum(self.images[y1:y2, x1:x2, ...], axis=(0, 1))

        val_min = np.min(image)
        val_max = np.max(image)

        image = 255 * (image - val_min) / (val_max - val_min) 
        image = image.astype(np.uint8)

        img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        q_img = QImage(img.data, self.w_image, self.h_image, 3*self.w_image,
                       QImage.Format.Format_RGB888) 

        self.pixmap_original = QPixmap().fromImage(q_img)

        self.image_label_size = self.image_label.size()
        self.pixmap = self.pixmap_original.scaled(self.image_label_size,
                                                  Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)

        self.image_label.setPixmap(self.pixmap)

        self.update_display()
        

    def resizeEvent(self, event):
        """
        Handle resize events.
        Properly resize the diffraction image while maintaining its aspect
        ratio. Annotation elements are redrawn in their appropriate positions.
        """

        super().resizeEvent(event)

        if self.pixmap_original is None:
            return
        
        self.image_label_size = self.image_label.size()
        
        self.pixmap = self.pixmap_original.scaled(self.image_label_size,
                                                  Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)

        pixmap_center = self.pixmap.rect().center()
        
        self.dx = self.image_label_size.width() // 2 - pixmap_center.x()
        self.dy = self.image_label_size.height() // 2 - pixmap_center.y()

        self.pixmap_w = self.pixmap.width()
        self.pixmap_h = self.pixmap.height()

        for i, sp in enumerate(self.spots):
            xx, yy = self.spot_coords[i]
            sp["coords"] = self.coord2pixel(xx, yy)

        self.update_display()
        

    def move_cursor(self, event):
        """
        Handle mouse movement within the diffraction image.
        A circle dynamically follows the cursor, and a label displays
        the corresponding normalized coordinates in real-time.
        """

        if self.pixmap is None:
            return

        x, y = event.x(), event.y()
        self.cursor_pos = (x, y)

        xx, yy = self.pixel2coord(x-self.dx, y-self.dy)

        self.coord_display.setText(f"Coordinates: ({xx:6.3f}, {yy:6.3f})")
        self.update_display()


    def toggle_select_mode(self, state):
        """
        Toggle the select mode based on the checkbox state.
        """

        if state == Qt.Checked:
            self.select_mode = True
        else:
            self.select_mode = False


    def keyPressEvent(self, event):
        """
        Handle key press events.
        Activate selection mode when the Shift key is pressed.
        """

        if event.key() == Qt.Key_Shift:
            self.select_mode = True
            self.select_chkbox.setChecked(True)
        super().keyPressEvent(event)

        
    def keyReleaseEvent(self, event):
        """
        Handle key release events.
        Deactivate selection mode when the Shift key is released.
        """

        if event.key() == Qt.Key_Shift:
            self.select_mode = False
            self.select_chkbox.setChecked(False)
        super().keyReleaseEvent(event)


    def on_click(self, event):
        """
        Handle click events on the diffraction image based on the selection mode.

        - When selection mode is OFF:
        Add a circular marker at the clicked location and update the spot lists.

        - When selection mode is ON:
        Toggle the selection state of a nearby spot if the click occurs close to it.
        """

        if self.pixmap is None:
            return

        if event.button() == Qt.LeftButton:
            x, y = event.x()-self.dx, event.y()-self.dy

            xx, yy = self.pixel2coord(x, y)

            if 1.0 < np.abs(xx) or 1.0 < np.abs(yy):
                return
            
            if self.select_mode:
                r2 = self.spot_size ** 2
                for i, sp in enumerate(self.spots):
                    xp, yp = sp['coords']
                    dx = x - xp
                    dy = y - yp
                    if dx*dx + dy*dy <= r2:
                        sp['selected'] = not sp['selected']
                        self.coord_list.item(i).setSelected(sp['selected'])
                        break

            else:
                self.spot_coords.append((xx, yy))

                self.spots.append({"coords": (x, y), "selected": False})

                self.coord_list.addItem(f"({xx:6.3f}, {yy:6.3f})")

                self.update_display()


    def update_spot_size(self, value):
        """
        Adjust the marker size for spots using the spinbox control
        """

        self.spot_size = value
        self.update_display()


    def toggle_spots(self, state):
        """
        Toggle the display of the spot marker based on the checkbox state
        """

        if state == Qt.Checked:
            self.show_spots = True
        else:
            self.show_spots = False
        self.update_display()


    def highlight_spots(self):
        """
        Highlight the spot markers that are selected in the list widget
        """

        if 0 == len(self.spot_coords):
            return
        
        selected_indexes = [item.row() for item in self.coord_list.selectedIndexes()]

        for i, sp in enumerate(self.spots):
            sp["selected"] = i in selected_indexes

        self.update_display()


    def delete_selected(self):
        """
        Delete the selected spot markers and refresh all related spot data
        structures
        """

        if 0 == len(self.spot_coords):
            return

        selected_indexes = sorted([item.row() for item in self.coord_list.selectedIndexes()], reverse=True)

        for idx in selected_indexes:
            del self.spots[idx]
            del self.spot_coords[idx]
            self.coord_list.takeItem(idx)

        self.update_display()


    def load_prev_image(self):
        """
        Load the previous diffraction pattern image from the 4D STEM dataset
        """

        if self.pixmap is None:
            return

        self.image_index -= 1
        if self.image_index < 0:
            self.image_index = self.num_images - 1
        self.load_image(self.image_index)

        if self.viewer_window is not None:
            xx = self.image_index % self.num_col
            yy = self.image_index // self.num_col
            self.viewer_window.select_index(xx, yy)
            if not self.viewer_window.isVisible():
                self.viewer_window.show()


    def load_next_image(self):
        """
        Load the next diffraction pattern image from the 4D STEM dataset
        """

        if self.pixmap is None:
            return

        self.image_index += 1
        if self.image_index >= self.num_images:
            self.image_index = 0
        self.load_image(self.image_index)

        if self.viewer_window is not None:
            xx = self.image_index % self.num_col
            yy = self.image_index // self.num_col
            self.viewer_window.select_index(xx, yy)
            if not self.viewer_window.isVisible():
                self.viewer_window.show()


    def update_display(self):
        """
        Dynamically update the diffraction image rendering in response to user
        interactions and state changes
        """

        if self.pixmap is None:
            return

        temp_pixmap = self.pixmap.copy()
        painter = QPainter(temp_pixmap)
        pen = QPen()
        pen.setWidth(5)

        s = self.spot_size

        if self.show_spots:
            for sp in self.spots:
                x, y = sp['coords']
                pen.setColor(QColor('red') if sp.get('selected') else QColor('green'))
                painter.setPen(pen)
                painter.drawEllipse(x - s // 2, y - s // 2, s, s)

        if self.cursor_pos:
            pen.setColor(QColor('blue'))
            painter.setPen(pen)
            x, y = self.cursor_pos
            x -= self.dx
            y -= self.dy
            painter.drawEllipse(x - s // 2, y - s // 2, s, s)

        painter.end()
        self.image_label.setPixmap(temp_pixmap)


    def pixel2coord(self, xp, yp):
        """
        Calculate the normalized coordinates from diffraction image pixel
        coordinates.
        """

        x = (2*xp - self.pixmap_w) / self.pixmap_w  
        y = -(2*yp - self.pixmap_h) / self.pixmap_h  

        return (x, y)


    def coord2pixel(self, xx, yy):
        """
        Calculate the pixel coordinates in diffraction image from normalized
        coordinates.
        """

        xp = int(0.5 * self.pixmap_w * (xx + 1.0))
        yp = int(0.5 * self.pixmap_h * (1.0 - yy))  

        return (xp, yp)
