from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QSlider, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PIL import Image, ImageFilter, ImageQt

from .get_resources import template_data

PREVIEW_HEIGHT = 170
PREVIEW_WIDTH = 278

class EditOptionsWidget(QWidget):
    def __init__(self):
        super(EditOptionsWidget, self).__init__()

        layout = QVBoxLayout()
        
        # Private class attributes
        self.previewer = None
        self.logger = None
        self.selected_template = None
        self.config = None
        self.number_of_columns = 1
        self.image_width = 1
        self.image_height = 1
        self.label_data = {}
        self.selected_row = None
        self.selected_col = None

        # Read template configuration
        self.template_config = template_data

        # Image selector
        self.image_selector_btn = QPushButton("Select Image")
        self.image_selector_btn.clicked.connect(self.select_image)

        # Preview for selected image
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("background-color: white;")

        # Layout for image selection and preview with centering
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_selector_btn)
        image_layout.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        # Logo selection dropdown
        self.logo_selector = QComboBox()
        self.logo_selector.setFixedWidth(350)
        self.logo_selector.addItems(["None", "ESPuino", "Tonuino"])

        # Blur strength slider
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setFixedWidth(350)
        self.blur_slider.setTickInterval(10)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setSliderPosition(20)
        
        # Line edit wdiget
        text_line = QLineEdit()
        text_line.setFixedWidth(350)
        
        # Custom text box
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text Label:"))
        text_layout.addWidget(text_line)
        
        # Horizontal layout for logo
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(QLabel("Select Logo:"))
        logo_layout.addWidget(self.logo_selector)
        
        # Horizontal layout for blur
        logo_blur = QHBoxLayout()
        logo_blur.addWidget(QLabel("Blur Strength:"))
        logo_blur.addWidget(self.blur_slider)
        
        # Image selector
        self.label_image_generator_btn = QPushButton("Generate and apply sticker")
        self.label_image_generator_btn.clicked.connect(self.generate_image)
        
        # Layout for image generator button
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.label_image_generator_btn)
        
        # Add all layouts to the main layout
        layout.addLayout(image_layout)
        layout.addLayout(text_layout)
        layout.addLayout(logo_layout)
        layout.addLayout(logo_blur)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
    def registerPreviewer(self, previewer):
        self.previewer = previewer
        
    def registerLogger(self, logger):
        self.logger = logger
        
    def select_template(self, template_name):
        self.selected_template = template_name
        self.config = self.template_config[template_name]
        self.number_of_columns = self.config["sticker_pattern"][1]
        self.image_width = self.config["sticker_width"]
        self.image_height = self.config["sticker_height"]
        self.label_data = {}
    
    def label_selected(self, index):
        row = index // self.number_of_columns
        col = index % self.number_of_columns
        self.selected_row = row
        self.selected_col = col
        self.draw_original_image(row, col)
        
    def generate_image(self) -> None:
        # Selected label
        row = self.selected_row
        col = self.selected_col
        
        if (row, col) not in self.label_data:
            QMessageBox.critical(self, "Generation Failed", "Please select image for this label first.")
            self.clear_image()
            return
    
        original_image = self.label_data[(row, col)]['original']
        
        # Apply the blur effect using the chosen strength
        blur_strength = self.blur_slider.value()
        blurred_image = original_image.filter(ImageFilter.GaussianBlur(blur_strength))

        # Convert the blurred image to a QPixmap
        blurred_qimage = ImageQt.ImageQt(blurred_image)
        blurred_pixmap = QPixmap.fromImage(blurred_qimage)
        blurred_pixmap = blurred_pixmap.scaled(
            PREVIEW_WIDTH, PREVIEW_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Scale the original image to fit the required height with aspect ratio
        target_height = PREVIEW_HEIGHT
        scale_factor = target_height / original_image.height
        scaled_width = int(original_image.width * scale_factor)

        # Convert scaled original image to QPixmap
        scaled_image = original_image.resize((scaled_width, target_height), Image.Resampling.LANCZOS)
        scaled_qimage = ImageQt.ImageQt(scaled_image)
        scaled_pixmap = QPixmap.fromImage(scaled_qimage)

        # Create a final pixmap for output
        final_pixmap = QPixmap(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        final_pixmap.fill(Qt.GlobalColor.white)

        # Draw the blurred background
        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, blurred_pixmap)

        # Center the scaled image over the blurred background
        x_offset = (PREVIEW_WIDTH - scaled_pixmap.width()) // 2
        painter.drawPixmap(x_offset, 0, scaled_pixmap)

        # End painting
        painter.end()

        # Set the preview
        self.image_preview.setPixmap(final_pixmap)
        
        # Final composition
        self.label_data[(row, col)]['final'] = ImageQt.fromqpixmap(final_pixmap)
        
        # Update the image in the preview widget
        if self.previewer:
            # Convert final pixmap to QImage
            final_qimage = final_pixmap.toImage()
            self.previewer.updateStickerImage(final_qimage)
    
    def draw_original_image(self) -> None:
        # Selected label
        row = self.selected_row
        col = self.selected_col
        
        # Get original image from label data
        if (row, col) not in self.label_data:
            self.clear_image()
            return
    
        if 'final' in self.label_data[(row, col)]:
            original_image = self.label_data[(row, col)]['final']
        else:
            original_image = self.label_data[(row, col)]['original']
                       
        # Scale the original image to fit the required height with aspect ratio
        target_height = PREVIEW_HEIGHT
        scale_factor = target_height / original_image.height
        scaled_width = int(original_image.width * scale_factor)
        
        # Convert scaled original image to QPixmap
        scaled_image = original_image.resize((scaled_width, target_height), Image.Resampling.LANCZOS)
        scaled_qimage = ImageQt.ImageQt(scaled_image)
        scaled_pixmap = QPixmap.fromImage(scaled_qimage)

        # Create a final pixmap for output
        final_pixmap = QPixmap(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        final_pixmap.fill(Qt.GlobalColor.white)

        # Draw the blurred background
        painter = QPainter(final_pixmap)

        # Center the scaled image over the blurred background
        x_offset = (PREVIEW_WIDTH - scaled_pixmap.width()) // 2
        painter.drawPixmap(x_offset, 0, scaled_pixmap)

        # End painting
        painter.end()

        # Set the preview
        self.image_preview.setPixmap(final_pixmap)
        
    def clear_image(self) -> None:
        # Create a final pixmap for output
        final_pixmap = QPixmap(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        final_pixmap.fill(Qt.GlobalColor.white)

        # Draw the blurred background
        painter = QPainter(final_pixmap)

        # End painting
        painter.end()

        # Set the preview
        self.image_preview.setPixmap(final_pixmap)

    def select_image(self) -> None:
        
        if self.selected_col is None or self.selected_row is None:
            QMessageBox.critical(self, "Image Selection Failed", "Please select a label in the preview image first.")
            self.clear_image()
            return
        
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select an Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            row = self.selected_row
            col = self.selected_col 
            
            self.label_data[(row, col)] = {}
            self.label_data[(row, col)]['path'] = file_name
            self.label_data[(row, col)]['original'] = Image.open(file_name)
            self.draw_original_image()