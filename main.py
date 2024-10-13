
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
from PyQt5 import uic, QtGui


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        self.default_file = "./rsc/black_image_640x480.jpg"
        self.current_file = self.default_file

        print("Initializing MyGUI...")
        uic.loadUi("image_viewer.ui", self)
        self.show()

        pixmap = QtGui.QPixmap(self.current_file)
        pixmap = pixmap.scaled(self.width(), self.height())
        self.label.setPixmap(pixmap)
        self.label.setMinimumSize(1, 1)

        self.file_list = None
        self.file_counter = None
        self.actionOpen_Image.triggered.connect(self.open_image)
        self.actionOpen_Directory.triggered.connect(self.open_directory)
        self.pushButton_previous.clicked.connect(self.previous_image)
        self.pushButton_next.clicked.connect(self.next_image)

    def resizeEvent(self, a0):
        try:
            pixmap = QtGui.QPixmap(self.current_file)
        except:
            pixmap = QtGui.QPixmap(self.default_file)

        pixmap = pixmap.scaled(self.width(), self.height())
        self.label.setPixmap(pixmap)
        self.label.resize(self.width(), self.height())

    def open_image(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Image Files (*.png; *.jpg; *.jpeg; *tif; *tiff)",
                                                  options=options)
        if filename != "":
            self.current_file = filename
            pixmap = QtGui.QPixmap(self.current_file)
            # pixmap = pixmap.scaled(self.width(), self.height())
            self.label.setPixmap(pixmap)

    def open_directory(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.file_list = [directory + "/" + f for f in os.listdir(directory)
                          if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")]
        print(f'file_list: {self.file_list}')
        self.file_counter = 0
        self.current_file = self.file_list[self.file_counter]
        pixmap = QtGui.QPixmap(self.current_file)
        self.label.setPixmap(pixmap)

    def next_image(self):
        if self.file_counter is not None:
            self.file_counter += 1
            self.file_counter %= len(self.file_list)
            self.current_file = self.file_list[self.file_counter]
            print(f'current_file: {self.current_file}')
            pixmap = QtGui.QPixmap(self.current_file)
            self.label.setPixmap(pixmap)

    def previous_image(self):
        if self.file_counter is not None:
            self.file_counter -= 1
            self.file_counter %= len(self.file_list)
            self.current_file = self.file_list[self.file_counter]
            print(f'current_file: {self.current_file}')
            pixmap = QtGui.QPixmap(self.current_file)
            self.label.setPixmap(pixmap)


def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()


if __name__ == "__main__":
    main()