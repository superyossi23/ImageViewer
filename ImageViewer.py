from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel, QVBoxLayout, \
    QWidget
from PyQt5.QtGui import QPixmap, QWheelEvent, QPainter, QColor
from PyQt5.QtCore import Qt, QPointF
import sys


class ImageViewer(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()

        # Setup scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Load image
        self.pixmap = QPixmap(image_path)
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.pixmap_item)

        # Enable smooth transformation
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setMouseTracking(True)  # Enable mouse tracking
        # Enable dragging
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # Zoom factor
        self.zoom_factor = 1.25
        self.current_zoom = 1.0  # Track zoom level

        # Label to display color info
        self.color_label = QLabel("Color: N/A", self)
        self.color_label.setFixedWidth(200)
        self.color_label.setStyleSheet("background: white; padding: 5px; border: 1px solid black;")
        self.color_label.move(10, 10)  # Position label at top-left

    def wheelEvent(self, event: QWheelEvent):
        """Handles mouse wheel zooming while keeping cursor position."""
        zoom_in = event.angleDelta().y() > 0  # Positive for zoom in

        if zoom_in:
            factor = self.zoom_factor
        else:
            factor = 1 / self.zoom_factor

        # Get the cursor position in scene coordinates before zooming
        cursor_pos = self.mapToScene(event.pos())

        # Apply zoom
        self.scale(factor, factor)
        self.current_zoom *= factor

        # Get the cursor position in view after zooming
        new_cursor_pos = self.mapFromScene(cursor_pos)

        # Adjust scrollbars to keep cursor at the same position
        delta = new_cursor_pos - event.pos()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

    def mouseMoveEvent(self, event):
        """Track mouse position and display pixel color."""
        scene_pos = self.mapToScene(event.pos())  # Convert to scene coordinates
        x, y = int(scene_pos.x()), int(scene_pos.y())

        # Check if within image bounds
        if 0 <= x < self.pixmap.width() and 0 <= y < self.pixmap.height():
            image = self.pixmap.toImage()  # Convert pixmap to image for pixel access
            color = QColor(image.pixel(x, y))  # Get pixel color

            # Update label text and color preview
            self.color_label.setText(f"{color.name()} ({x}, {y})")
            self.color_label.setStyleSheet(f"background: white; padding: 1px; border: 4px solid {color.name()};")

        super().mouseMoveEvent(event)  # Keep other mouse functionalities


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer(r"C:\Users\t-mes\Pictures\27378389-番号-55、赤い円に.jpg")  # Replace with your image path
    viewer.setMouseTracking(True)  # Enable mouse tracking
    viewer.show()
    sys.exit(app.exec_())
