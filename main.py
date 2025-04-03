
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication, QHBoxLayout
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from ImageViewer import ImageViewer


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        print('S __init__')
        self.current_file = ''

        print("Initializing MyGUI...")
        uic.loadUi("image_viewer.ui", self)

        # Default image viewer with no image initially
        self.image_viewer = ImageViewer("")

        # Find the layout from the UI
        hlayout = self.findChild(QHBoxLayout, "horizontalLayout_Image")  # Adjust layout name if needed
        hlayout.addWidget(self.image_viewer)  # Add image viewer to the layout

        # FILE HANDLING
        self.file_list = None
        self.file_counter = None
        self.actionOpen_Image.triggered.connect(self.open_image)
        self.actionOpen_Directory.triggered.connect(self.open_directory)
        self.pushButton_previous.clicked.connect(self.previous_image)
        self.pushButton_next.clicked.connect(self.next_image)

        # Enable drag and drop
        self.setAcceptDrops(True)

        self.show()
        print('E __init__')

    #################################
    # FILE HANDLING
    #################################
    def change_scene(self, new_file):
        try:
            self.image_viewer.scene.clear()  # Clear previous image
            self.image_viewer.pixmap = QPixmap(new_file)
            self.image_viewer.pixmap_item = self.image_viewer.scene.addPixmap(self.image_viewer.pixmap)
            self.image_viewer.setScene(self.image_viewer.scene)
        except Exception as e:
            print(f"[change_scene] Error: {e}")

    def resizeEvent(self, event):
        """Resize event handler to adjust the image when the window is resized."""
        try:
            super().resizeEvent(event)  # Call parent class's resizeEvent

            # Check if pixmap exists before resizing
            if self.image_viewer.pixmap and not self.image_viewer.pixmap.isNull():
                self.image_viewer.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.change_scene(self.image_path)

        except Exception as e:
            print(f"[resizeEvent] Error: {e}")

    def open_image(self):
        print('S open_image')
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Image Files (*.png; *.jpg; *.jpeg; *tif; *tiff)",
                                                  options=options)
        if filename != "":
            self.current_file = filename
            self.image_viewer.scene.clear()  # Clear previous image
            self.change_scene(self.current_file)

        print('E open_image')

    def open_directory(self):
        print('S open_directory')
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.file_list = [directory + "/" + f for f in os.listdir(directory)
                          if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")]
        print(f'file_list: {self.file_list}')
        self.file_counter = 0
        self.current_file = self.file_list[self.file_counter]
        self.change_scene(self.current_file)

        print('E open_directory')

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

    #################################
    # DRAG AND DROP
    #################################
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events if they contain an image file."""
        print('S dragEnterEvent')
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tif")):
                event.acceptProposedAction()
        else:
            event.ignore()
        print('E dragEnterEvent')

    def dropEvent(self, event: QDropEvent):
        """Handle dropped image file."""
        print('S dropEvent')
        self.file_list = []

        urls = event.mimeData().urls()
        if urls:
            for i, url in enumerate(urls):
                print(f'url: {url}')
                file_path = url.toLocalFile()  # Get a file path
                print(f'{i} file_path: {file_path}')
                self.file_list.append(file_path)

            self.current_file = self.file_list[0]
            self.change_scene(self.current_file)

        print('E dropEvent')


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()


if __name__ == "__main__":
    main()