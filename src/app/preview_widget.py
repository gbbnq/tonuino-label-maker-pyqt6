from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsPixmapItem
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainter, QPixmap, QImage, QBrush, QColor

import app
from .get_resources import template_data

# Scale factor for UI rendering
SCALE_FACTOR = 5

class PreviewWidget(QWidget):

    def __init__(self):
        super(PreviewWidget, self).__init__()
        
        # Private class attributes
        self.editor = None
        self.logger = None
        self.labels = {}

        # Read template configuration
        self.template_config = template_data

        # Initialize graphics scene and view
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        
    def registerEditor(self, editor:app.EditOptionsWidget):
        """Register the editor widget

        Args:
            editor (ui.EditOptionsWidget): Instance of editor widget class
        """
        self.editor = editor
        
    def registerLogger(self, logger:app.FooterWidget):
        """Register the logger widget

        Args:
            logger (ui.FooterWidget): Instance of logger widget class
        """
        self.logger = logger

    def select_template(self, template_name:str) -> None:
        """Process new template selection

        Args:
            template_name (str): Template name
        """
        self.selected_template = template_name
        self.config = self.template_config[template_name]
        self.render_template(self.selected_template)

    def render_template(self, template_name:str) -> None:
        """Render template in preview canvas

        Args:
            template_name (str): Name of selected template
        """
        self.scene.clear()
        self.labels = {}

        if template_name not in self.template_config:
            return

        pattern = self.config["sticker_pattern"]
        top_margin = self.config["top_margin"] * SCALE_FACTOR
        left_margin = self.config["left_margin"] * SCALE_FACTOR
        sticker_width = self.config["sticker_width"] * SCALE_FACTOR
        sticker_height = self.config["sticker_height"] * SCALE_FACTOR
        h_margin = self.config["horizontal_margin"] * SCALE_FACTOR
        v_margin = self.config["vertical_margin"] * SCALE_FACTOR

        # Draw labels
        for row in range(pattern[0]):
            for col in range(pattern[1]):
                x = left_margin + col * (sticker_width + h_margin)
                y = top_margin + row * (sticker_height + v_margin)
                
                label_rect = QRectF(x, y, sticker_width, sticker_height)
                label = QGraphicsRectItem(label_rect)
                label.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
                label.setToolTip(f"Label {row + 1},{col + 1}")
                self.scene.addItem(label)
                label.setZValue(1)
                self.labels[(row, col)] = label

                # Connect to clicks
                label.mousePressEvent = lambda _, r=row, c=col: self.select_sticker(r, c)
                
        # Draw A4 paper
        label_rect = QRectF(0, 0, 210 * SCALE_FACTOR, 297 * SCALE_FACTOR)
        label = QGraphicsRectItem(label_rect)
        label.setBrush(QBrush(QColor(255, 255, 255, 255)))
        self.scene.addItem(label)
                
        # Set scene view
        self.view.setScene(self.scene)
        self.view.setSceneRect(self.scene.itemsBoundingRect())
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.resetTransform()
        self.view.scale(1 / SCALE_FACTOR, 1 / SCALE_FACTOR)

    def select_sticker(self, row:int, col:int) -> None:
        """Emit the selected row and column

        Args:
            row (int): Selected row
            col (int): Selected column
        """
        self.editor.selected_row = row
        self.editor.selected_col = col
        self.editor.draw_original_image()

    def updateStickerImage(self, image:QImage) -> None:
        """Renders generated label image in preview scene

        Args:
            image (QImage): QImage instance containing generated label image
        """
        # Get rect dimensions
        rect = self.labels[(self.editor.selected_row, self.editor.selected_col)].rect()
        
        # Create a QBrush with the QImage converted to QPixmap
        pixmap = QPixmap.fromImage(image)
        
        # Scale the pixmap while maintaining aspect ratio
        target_height = int(rect.height())
        scaled_pixmap = pixmap.scaledToHeight(target_height, mode=Qt.TransformationMode.SmoothTransformation)

        # Calculate position to center the QPixmap in the QGraphicsRectItem
        pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
        pixmap_item.setPos(
            rect.left() + (rect.width() - scaled_pixmap.width()) / 2,
            rect.top() + (rect.height() - scaled_pixmap.height()) / 2
        )

        # Add the pixmap item to the scene
        self.scene.addItem(pixmap_item)