
import os
from PySide6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication, QHBoxLayout, QMenu
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QAction

from ImageViewer import ImageViewer


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        print('S __init__')
        self.current_file = ''

        print("Initializing MyGUI...")
        ui_file = QFile("image_viewer.ui")
        if not ui_file.open(QFile.ReadOnly):
            print("Failed to open UI file: image_viewer.ui")
        else:
            loader = QUiLoader()
            loaded_ui = loader.load(ui_file)
            ui_file.close()
            if loaded_ui:
                # Transfer main UI parts into this QMainWindow
                if loaded_ui.centralWidget():
                    self.setCentralWidget(loaded_ui.centralWidget())
                if loaded_ui.menuBar():
                    self.setMenuBar(loaded_ui.menuBar())

                # Ensure actions exist: QUiLoader may not create QAction objects from .ui files.
                # Find the File menu and create actions if they are missing, then attach them.
                try:
                    menu_file = self.findChild(QMenu, 'menuFile')
                    if menu_file is not None:
                        # Inspect submenu actions; if they are not present, create them
                        names = {a.objectName(): a for a in menu_file.actions()}
                        if 'actionOpen_Image' not in names:
                            a = QAction('Open Image', self)
                            a.setObjectName('actionOpen_Image')
                            menu_file.addAction(a)
                        if 'actionOpen_Directory' not in names:
                            a = QAction('Open Directory', self)
                            a.setObjectName('actionOpen_Directory')
                            menu_file.addAction(a)
                        if 'actionQuit' not in names:
                            a = QAction('Quit', self)
                            a.setObjectName('actionQuit')
                            menu_file.addAction(a)
                except Exception:
                    pass
                if loaded_ui.statusBar():
                    self.setStatusBar(loaded_ui.statusBar())

                # Wire commonly-used children to attributes used elsewhere in the code
                # Try to find the layout and widgets on the loaded UI first, then fall back to searching on `self`.
                hlayout = loaded_ui.findChild(QHBoxLayout, "horizontalLayout_Image")
                if hlayout is None:
                    hlayout = self.findChild(QHBoxLayout, "horizontalLayout_Image")
                self.horizontalLayout_Image = hlayout

                self.actionOpen_Image = loaded_ui.findChild(QAction, "actionOpen_Image") or self.findChild(QAction, "actionOpen_Image")
                self.actionOpen_Directory = loaded_ui.findChild(QAction, "actionOpen_Directory") or self.findChild(QAction, "actionOpen_Directory")
                self.pushButton_previous = loaded_ui.findChild(QPushButton, "pushButton_previous") or self.findChild(QPushButton, "pushButton_previous")
                self.pushButton_next = loaded_ui.findChild(QPushButton, "pushButton_next") or self.findChild(QPushButton, "pushButton_next")
            else:
                print("QUiLoader failed to load UI")

        # Default image viewer with no image initially
        self.image_viewer = ImageViewer("")

        # Find the layout from the UI (use attribute set earlier) and add the viewer
        hlayout = getattr(self, 'horizontalLayout_Image', None)
        if hlayout is None:
            hlayout = self.findChild(QHBoxLayout, "horizontalLayout_Image")

        if hlayout is not None:
            try:
                hlayout.addWidget(self.image_viewer)
            except Exception:
                print("Failed to add ImageViewer to layout")
        else:
            print("horizontalLayout_Image not found in UI; cannot add ImageViewer")

        # FILE HANDLING
        self.file_list = None
        self.file_counter = None
        # Ensure actions exist and connect signals. QUiLoader may not create QAction objects.
        try:
            menu_file = self.findChild(QMenu, 'menuFile')
            if menu_file is not None:
                def ensure_action(name, text):
                    a = self.findChild(QAction, name)
                    if a is None:
                        a = QAction(text, self)
                        a.setObjectName(name)
                        menu_file.addAction(a)
                    return a

                self.actionOpen_Image = ensure_action('actionOpen_Image', 'Open Image')
                self.actionOpen_Directory = ensure_action('actionOpen_Directory', 'Open Directory')
                self.actionQuit = ensure_action('actionQuit', 'Quit')

            # Connect signals only if the widgets/actions were found/created
            if getattr(self, 'actionOpen_Image', None) is not None:
                try:
                    self.actionOpen_Image.triggered.connect(self.open_image)
                except Exception:
                    pass
            if getattr(self, 'actionOpen_Directory', None) is not None:
                try:
                    self.actionOpen_Directory.triggered.connect(self.open_directory)
                except Exception:
                    pass
            if getattr(self, 'actionQuit', None) is not None:
                try:
                    self.actionQuit.triggered.connect(lambda: QApplication.instance().quit())
                except Exception:
                    pass
        except Exception:
            # Fallback: keep original behavior if anything goes wrong
            if getattr(self, 'actionOpen_Image', None) is not None:
                try:
                    self.actionOpen_Image.triggered.connect(self.open_image)
                except Exception:
                    pass
            if getattr(self, 'actionOpen_Directory', None) is not None:
                try:
                    self.actionOpen_Directory.triggered.connect(self.open_directory)
                except Exception:
                    pass
        if getattr(self, 'pushButton_previous', None) is not None:
            try:
                self.pushButton_previous.clicked.connect(self.previous_image)
            except Exception:
                pass
        if getattr(self, 'pushButton_next', None) is not None:
            try:
                self.pushButton_next.clicked.connect(self.next_image)
            except Exception:
                pass

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
            if getattr(self.image_viewer, 'pixmap', None) and not self.image_viewer.pixmap.isNull():
                try:
                    self.image_viewer.fitInView(self.image_viewer.scene.sceneRect(), Qt.KeepAspectRatio)
                except Exception:
                    pass
                # If we have a current file, reload or adjust the scene
                if getattr(self, 'current_file', None):
                    self.change_scene(self.current_file)

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
    app.exec()


if __name__ == "__main__":
    main()
    print("Exiting main.py")
    