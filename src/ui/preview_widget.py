import os

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsPixmapItem
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QRectF, QMarginsF
from PyQt6.QtGui import QBrush, QPainter, QPageLayout, QPixmap, QImage
from PyQt6.QtPrintSupport import QPrinter

import ui
from .get_resources import template_data

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
        
    def registerEditor(self, editor:ui.EditOptionsWidget):
        """Register the editor widget

        Args:
            editor (ui.EditOptionsWidget): Instance of editor widget class
        """
        self.editor = editor
        
    def registerLogger(self, logger:ui.FooterWidget):
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

    def render_template(self, template_name, scale_factor=5):
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
        
    def generate_pdf(self, project_path:str) -> bool:
        """Renders and stores pdf document

        Args:
            project_path (str): Project path

        Returns:
            bool: True, if sucessful
        """
        #FIXME: This is not scaling the paper properly
        try:
            # Set up the QPrinter to output in PDF format
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            pdf_path = os.path.join(project_path, "label_output.pdf")
            printer.setOutputFileName(pdf_path)
            printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
            
            # Standard A4 dimensions
            a4_width_points = 210
            a4_height_points = 297

            scene_rect = self.scene.sceneRect()
            
            # Set the printer page margins to zero to allow full-page printing
            

            # Set up QPainter
            painter = QPainter(printer)
            if not painter.isActive():
                self.logger.log("Failed to initialize printer. Please close file first.")
                return False
            
            """
            # Calculate scale factor based on scene and page to maintain aspect ratio
            x_scale = a4_width_points / scene_rect.width()
            y_scale = a4_height_points / scene_rect.height()
            scale = min(x_scale, y_scale)

            # Center output if necessary
            offset_x = (a4_width_points - scene_rect.width() * scale) / 2
            offset_y = (a4_height_points - scene_rect.height() * scale) / 2

            # Set transforms for centering and scaling
            painter.translate(offset_x, offset_y)
            painter.scale(scale, scale)

            # Use scene rendering method
            self.scene.render(painter)
            
            # Finish the painting process
            painter.end()

            self.logger.log(f"PDF successfully created at '{pdf_path}'")
            return True
            """
            # Reset transformations and set scene to full scale for PDF
            self.view.resetTransform()
            self.view.scale(1 / SCALE_FACTOR, 1 / SCALE_FACTOR)
            
            # Calculate scale for rendering to match printer page size
            scene_rect = self.scene.sceneRect()
            page_rect = printer.pageRect(QPrinter.Unit.Millimeter)

            x_scale = page_rect.width() / scene_rect.width()
            y_scale = page_rect.height() / scene_rect.height()
            
            painter.scale(x_scale, y_scale)
            self.scene.render(painter)
            painter.end()
            
            self.view.resetTransform()
            self.view.scale(1 / SCALE_FACTOR, 1 / SCALE_FACTOR)

            self.logger.log(f"PDF successfully created at '{pdf_path}'")
            return True

        except Exception as e:
            self.logger.log(f"Error generating PDF: {e}")
            return False