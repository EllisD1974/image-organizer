import os
import shutil
from pathlib import Path

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QListWidget, QMessageBox, QInputDialog, QListWidgetItem,
    QSizePolicy,
)


class ImageSorter(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("nel", "ImageSorterApp")
        self.category_root = self.settings.value("category_root", type=str)

        self.image_paths = []
        self.current_index = 0

        # --- UI ELEMENTS ---
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.btn_prev = QPushButton("Previous Image")
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_prev.setEnabled(False)

        self.btn_next = QPushButton("Next Image")
        self.btn_next.clicked.connect(self.next_image)
        self.btn_next.setEnabled(False)

        self.btn_move = QPushButton("Move Image → Selected Folder")
        self.btn_move.clicked.connect(self.move_image)
        self.btn_move.setEnabled(False)

        self.btn_select_dirs = QPushButton("Select Image Folder(s)")
        self.btn_select_dirs.clicked.connect(self.load_directories)

        self.btn_set_category_root = QPushButton("Set Category Root Folder")
        self.btn_set_category_root.clicked.connect(self.set_category_root)

        self.btn_new_category = QPushButton("Create New Category Folder")
        self.btn_new_category.clicked.connect(self.create_new_folder)
        self.btn_new_category.setEnabled(False)

        self.folder_list = QListWidget()

        # --- LAYOUT ---
        main_layout = QHBoxLayout(self)

        # LEFT: image + controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_label)

        nav_row = QHBoxLayout()
        nav_row.addWidget(self.btn_prev)
        nav_row.addWidget(self.btn_move)
        nav_row.addWidget(self.btn_next)
        left_layout.addLayout(nav_row)

        left_layout.addWidget(self.btn_select_dirs)
        left_layout.addWidget(self.btn_set_category_root)

        # RIGHT: category list + new category button
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Categories"))
        right_layout.addWidget(self.folder_list)
        right_layout.addWidget(self.btn_new_category)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)

        self.setWindowTitle("Image Sorter")
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Load categories if root was saved
        if self.category_root:
            self.load_category_folders()
            self.btn_new_category.setEnabled(True)

    # ----------------------------------------------------------------------

    def closeEvent(self, event):
        self.image_label.clear()
        self.image_label.setPixmap(QPixmap())  # release native image handles
        event.accept()

    def resizeEvent(self, event):
        if self.image_paths and self.current_index < len(self.image_paths):
            self.show_image()  # rescale current image
        super().resizeEvent(event)

    def load_directories(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if not directory:
            return

        # Accepted extensions
        valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}

        # Collect image file paths ONLY — no pixmaps yet
        paths = []
        for root, _, files in os.walk(directory):
            for f in files:
                if Path(f).suffix.lower() in valid_ext:
                    paths.append(os.path.join(root, f))

        paths.sort()  # OPTIONAL but makes navigation nicer

        if not paths:
            QMessageBox.warning(self, "No Images", "No images found in directory.")
            return

        self.image_paths = paths
        self.current_index = 0

        # Enable buttons now that we have images
        self.btn_move.setEnabled(True)
        self.btn_next.setEnabled(True)
        self.btn_prev.setEnabled(True)

        # Load the FIRST IMAGE ONLY
        self.show_image()

    # ----------------------------------------------------------------------

    def show_image(self):
        if not self.image_paths:
            self.image_label.setText("No images loaded")
            return

        img_path = self.image_paths[self.current_index]
        pixmap = QPixmap(img_path)

        if not pixmap.isNull():
            # Scale to the label's current size, keeping aspect ratio
            scaled_pix = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pix)
        else:
            self.image_label.setText("Failed to load image")

    # ----------------------------------------------------------------------

    def next_image(self):
        if not self.image_paths:
            return

        self.btn_prev.setEnabled(True)

        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image()
        else:
            self.btn_next.setEnabled(False)
            # QMessageBox.information(self, "End", "No more images.")

    def prev_image(self):
        if not self.image_paths:
            return

        self.btn_next.setEnabled(True)

        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
        else:
            self.btn_prev.setEnabled(False)
            # QMessageBox.information(self, "Start", "Already at first image.")

    # ----------------------------------------------------------------------

    def set_category_root(self):
        root = QFileDialog.getExistingDirectory(
            self, "Select Category Root Folder"
        )
        if not root:
            return

        self.category_root = root
        self.settings.setValue("category_root", root)
        self.load_category_folders()
        self.btn_new_folder.setEnabled(True)

    # ----------------------------------------------------------------------

    def load_category_folders(self):
        self.folder_list.clear()
        if not self.category_root:
            return

        folders = []

        # Collect ALL subdirectories
        for root, dirs, _ in os.walk(self.category_root):
            for d in dirs:
                full = os.path.join(root, d)
                rel = os.path.relpath(full, self.category_root)
                folders.append(rel)

        # Sort alphabetically by directory hierarchy
        folders.sort(key=lambda f: f.lower().split(os.sep))

        # Add to list with indentation AND store real path
        for rel in folders:
            depth = rel.count(os.sep)
            display_text = ("    " * depth) + rel  # indented display

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, rel)  # store REAL RELATIVE PATH
            self.folder_list.addItem(item)

    # ----------------------------------------------------------------------

    def create_new_folder(self):
        if not self.category_root:
            QMessageBox.warning(self, "Error", "Set a category root folder first.")
            return

        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if not ok or not name.strip():
            return

        new_path = Path(self.category_root) / name.strip()
        new_path.mkdir(parents=True, exist_ok=True)

        self.load_category_folders()

    # ----------------------------------------------------------------------

    def move_image(self):
        if not self.folder_list.currentItem():
            QMessageBox.warning(self, "No Folder", "Select a destination folder.")
            return

        # dest = self.folder_list.currentItem().text()
        # dest_path = Path(self.category_root) / dest

        rel = self.folder_list.currentItem().data(Qt.UserRole)
        dest_path = Path(self.category_root) / rel

        src = Path(self.image_paths[self.current_index])

        try:
            shutil.move(str(src), str(dest_path / src.name))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        # Remove moved image
        del self.image_paths[self.current_index]

        if self.current_index >= len(self.image_paths):
            self.image_label.setText("No more images!")
            return

        self.show_image()


# ======================================================================

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ImageSorter()
    w.show()
    sys.exit(app.exec_())
