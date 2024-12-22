from PIL import Image, ImageFilter, ImageQt, ImageDraw, ImageFont, ImageGrab
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QSlider, \
    QLineEdit, QMessageBox, QGroupBox

from .get_resources import template_data, espuino_logo, tonuino_logo

# Size the label to be scaled for the editor image canvas
PREVIEW_HEIGHT = 170
PREVIEW_WIDTH = 278


class EditOptionsWidget(QWidget):
    def __init__(self):
        super(EditOptionsWidget, self).__init__()

        layout = QVBoxLayout()
        
        # Private class attributes
        self.__previewer__ = None
        self.__logger__ = None
        self.image_width = 1
        self.image_height = 1
        self.label_data = {}
        
        # Public class attributes
        self.config = None
        self.selected_row = None
        self.selected_col = None

        # Read template configuration
        self.template_config = template_data

        self.image_load_group = QGroupBox("Load Image ...")
        self.image_load_layout = QHBoxLayout()

        # Load image from file
        self.image_selector_btn = QPushButton("From File")
        self.image_selector_btn.clicked.connect(self.select_image)
        # Load image from clipboard
        self.image_load_from_clipboard = QPushButton("From Clipboard")
        self.image_load_from_clipboard.clicked.connect(self.load_image_from_clipboard)

        self.image_load_layout.addWidget(self.image_selector_btn)
        self.image_load_layout.addWidget(self.image_load_from_clipboard)
        self.image_load_group.setLayout(self.image_load_layout)

        # Preview for selected image
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("background-color: white;")

        # Layout for image selection and preview with centering
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_load_group)
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
        self.text_line = QLineEdit()
        self.text_line.setFixedWidth(350)
        
        # Custom text box
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text Label:"))
        text_layout.addWidget(self.text_line)
        
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
        
    def registerPreviewer(self, previewer) -> None:
        """Register the preview widget

        Args:
            logger (ui.PreviewWidget): Instance of preview widget class
        """
        self.__previewer__ = previewer
        
    def registerLogger(self, logger) -> None:
        """Register the logger widget

        Args:
            logger (ui.FooterWidget): Instance of logger widget class
        """
        self.__logger__ = logger
        
    def select_template(self, template_name:str) -> None:
        """Set new template

        Args:
            template_name (str): Template name
        """
        self.config = self.template_config[template_name]
        self.image_width = self.config["sticker_width"]
        self.image_height = self.config["sticker_height"]
        # Clear existing label data
        self.label_data = {}
        
    def generate_image(self) -> None:
        """Generates label and updates template preview
        """
        # Selected label
        row = self.selected_row
        col = self.selected_col
        
        # Design parameters
        blur_strength = self.blur_slider.value()
        logo_setting = self.logo_selector.currentText()
        text_setting = self.text_line.text()
        
        if (row, col) not in self.label_data:
            QMessageBox.critical(self, "Generation Failed", "Please select image for this label first.")
            self.clear_image()
            return
    
        # Original un-scaled PIL image
        original_image = self.label_data[(row, col)]['original']
        
        # Convert dimensions from mm to inches and calculate required pixels for 150 DPI
        image_width_inch = self.image_width / 25.4
        image_height_inch = self.image_height / 25.4
        target_width_px = int(150 * image_width_inch)
        target_height_px = int(150 * image_height_inch)
        
        # Scale original image to the given height with the given DPI
        scale_factor = target_height_px / original_image.height
        scaled_width = int(original_image.width * scale_factor)
        
        # Ensure the image has an alpha channel if required
        if original_image.mode != "RGBA":
            original_image = original_image.convert("RGBA")
        
        original_scaled = original_image.resize((scaled_width, target_height_px), Image.Resampling.LANCZOS)
        
        # Create a blurred version of the original image
        blurred_image = original_image.filter(ImageFilter.GaussianBlur(blur_strength))

        # Scale the blurred image to match the target width while keeping aspect ratio
        scale_factor_blur = target_width_px / blurred_image.width
        blurred_scaled_height = int(blurred_image.height * scale_factor_blur)
        
        blurred_scaled = blurred_image.resize((target_width_px, blurred_scaled_height), Image.Resampling.LANCZOS)
        
        # Create a new image with the required target dimensions for print
        final_print_image = Image.new("RGBA", (target_width_px, target_height_px), (255, 255, 255, 0))
        
        # Paste the blurred image as the background
        final_print_image.paste(blurred_scaled, (0, 0))
        
        # Center the original scaled image over the blurred background
        x_offset = (target_width_px - scaled_width) // 2
        final_print_image.paste(original_scaled, (x_offset, 0), original_scaled)
        
        # Obtain logo based on logo_setting
        if logo_setting == "ESPuino":
            logo_image = espuino_logo
        elif logo_setting == "Tonuino":
            logo_image = tonuino_logo
        else:
            logo_image = None
            
        # Add the logo to the image
        if logo_image:
            logo_scale_factor = 0.1
            logo_target_width = int(target_width_px * logo_scale_factor)
            
            # Keep aspect ratio for the logo
            logo_scale_factor = logo_target_width / logo_image.width
            logo_target_height = int(logo_image.height * logo_scale_factor)
            logo_resized = logo_image.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
            
            # Paste the logo at the bottom-right corner
            logo_x = target_width_px - logo_resized.width - 10
            logo_y = target_height_px - logo_resized.height
            final_print_image.paste(logo_resized, (logo_x, logo_y), mask=logo_resized.split()[3])

        # Add text to the top if text_setting is not empty or None
        if text_setting:
            draw = ImageDraw.Draw(final_print_image)
            font_size = 30
            font = ImageFont.truetype("arial.ttf", font_size)
            
            # Calculate text size using textbbox
            bounding_box = draw.textbbox((0, 0), text_setting, font=font)
            text_width = bounding_box[2] - bounding_box[0]
            text_height = bounding_box[3] - bounding_box[1]
            
            # Adjust font size if necessary
            max_text_width = target_width_px * 0.9  # Ensure text doesn't span too wide
            if text_width > max_text_width:
                font_size = int(max_text_width / text_width * font_size)
                font = ImageFont.truetype("arial.ttf", font_size)
                bounding_box = draw.textbbox((0, 0), text_setting, font=font)
                text_width = bounding_box[2] - bounding_box[0]
                text_height = bounding_box[3] - bounding_box[1]

            # Position and draw the text
            text_x = (target_width_px - text_width) // 2
            text_y = 10  # Position from top
            
            # Determine text color based on the brightness of the top section of the blurred image
            top_region = blurred_scaled.crop((0, 0, target_width_px, text_height)).convert("L")
            total_brightness = sum(top_region.getdata())
            avg_brightness = total_brightness / (top_region.width * top_region.height)
            
            # Choose white text if the background is dark, otherwise black
            text_color = (255, 255, 255, 255) if avg_brightness < 128 else (0, 0, 0, 255)

            # Draw the text on the image
            draw.text((text_x, text_y), text_setting, font=font, fill=text_color)

        # Store the final composition for printing
        self.label_data[(row, col)]['final_print'] = final_print_image
        
        # Prepare for UI: convert the final_print image to a scaled QPixmap
        final_print_qimage = ImageQt.ImageQt(final_print_image)
        final_pixmap = QPixmap.fromImage(final_print_qimage)
        final_pixmap = final_pixmap.scaled(
            PREVIEW_WIDTH, PREVIEW_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Set the preview image
        self.image_preview.setPixmap(final_pixmap)
        
        # Log
        if self.__logger__:
            self.__logger__.log(f"Generated label for ({row+1}, {col+1})")
        
        # Update the image in the preview widget
        if self.__previewer__:
            self.__previewer__.updateStickerImage(final_print_qimage)
    
    def draw_original_image(self) -> None:
        """Draws image from label data to editor image canvas
        """
        # Selected label
        row = self.selected_row
        col = self.selected_col
        
        # Get original image from label data
        if (row, col) not in self.label_data:
            self.clear_image()
            return
    
        if 'final_print' in self.label_data[(row, col)]:
            original_image = self.label_data[(row, col)]['final_print']
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
        """Displays empty image canvas in label editor
        """
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
        """Opens selected image using PIL stores image in label data
        """
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
            
            if self.__logger__:
                self.__logger__.log(f"Loaded image {file_name} for label ({row + 1},{col + 1})")

    def load_image_from_clipboard(self) -> None:
        """Load image form clipboard
        """
        if self.selected_col is None or self.selected_row is None:
            QMessageBox.critical(self, "Image Selection Failed", "Please select a label in the preview image first.")
            self.clear_image()
            return

        data = ImageGrab.grabclipboard()
        if data:
            if isinstance(data, Image.Image):
                # Load image directly from clipboard
                row = self.selected_row
                col = self.selected_col

                self.label_data[(row, col)] = {}
                self.label_data[(row, col)]['original'] = data
                self.draw_original_image()

                if self.__logger__:
                    self.__logger__.log(f"Loaded image from clipboard for label ({row + 1},{col + 1})")

            if isinstance(data, list):
                raise NotImplementedError(
                    "Loading single/multiple file pathlist from clipboard is currently not supported")
