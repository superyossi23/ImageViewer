
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication, QHBoxLayout
from PyQt5 import uic, QtGui, QtCore

from ImageViewer import ImageViewer


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        self.default_file = "./rsc/black_image_640x480.jpg"
        self.current_file = self.default_file

        print("Initializing MyGUI...")
        uic.loadUi("image_viewer.ui", self)

        # Default image viewer with no image initially
        self.image_viewer = ImageViewer("")

        # Find the layout from the UI
        hlayout = self.findChild(QHBoxLayout, "horizontalLayout_Image")  # Adjust layout name if needed
        hlayout.addWidget(self.image_viewer)  # Add image viewer to the layout

        self.file_list = None
        self.file_counter = None
        self.actionOpen_Image.triggered.connect(self.open_image)
        self.actionOpen_Directory.triggered.connect(self.open_directory)
        self.pushButton_previous.clicked.connect(self.previous_image)
        self.pushButton_next.clicked.connect(self.next_image)

        self.show()

    def resizeEvent(self, event):
        """Resize event handler to adjust the image when the window is resized."""
        try:
            super().resizeEvent(event)  # Call parent class's resizeEvent

            # Check if pixmap exists before resizing
            if self.image_viewer.pixmap and not self.image_viewer.pixmap.isNull():
                self.image_viewer.fitInView(self.image_viewer.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
                self.change_scene(self.current_file)

        except Exception as e:
            print(f"Error during resize event: {e}")  # Print error for debugging

    def open_image(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Image Files (*.png; *.jpg; *.jpeg; *tif; *tiff)",
                                                  options=options)
        if filename != "":
            self.current_file = filename
            self.image_viewer.scene.clear()  # Clear previous image
            self.change_scene(self.current_file)

    def open_directory(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.file_list = [directory + "/" + f for f in os.listdir(directory)
                          if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")]
        print(f'file_list: {self.file_list}')
        self.file_counter = 0
        self.current_file = self.file_list[self.file_counter]
        self.change_scene(self.current_file)

    def next_image(self):
        if self.file_counter is not None:
            self.file_counter += 1
            self.file_counter %= len(self.file_list)
            self.current_file = self.file_list[self.file_counter]
            print(f'[next_image]: {self.current_file}')
            self.change_scene(self.current_file)

    def previous_image(self):
        if self.file_counter is not None:
            self.file_counter -= 1
            self.file_counter %= len(self.file_list)
            self.current_file = self.file_list[self.file_counter]
            print(f'[previous_image]: {self.current_file}')
            self.change_scene(self.current_file)

    def change_scene(self, new_file):
        self.image_viewer.scene.clear()  # Clear previous image
        self.image_viewer.pixmap = QtGui.QPixmap(new_file)
        self.image_viewer.pixmap_item = self.image_viewer.scene.addPixmap(self.image_viewer.pixmap)
        self.image_viewer.setScene(self.image_viewer.scene)


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()


if __name__ == "__main__":
    main()