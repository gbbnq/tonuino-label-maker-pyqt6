from PIL import Image

class PDFCreator:
    def __init__(self, dpi=150):
        # Public class attributes
        self.dpi = dpi
        
        # Constants for A4 page size at 150 DPI
        self.a4_width_px = int(210 / 25.4 * dpi)  # Convert mm to inches and multiply by 150 dpi
        self.a4_height_px = int(297 / 25.4 * dpi)

    def create_label_page(self, label_data:dict, top_margin:float, left_margin:float, sticker_pattern:tuple,
                          sticker_width:float, sticker_height:float, horizontal_margin:float, vertical_margin:float) -> Image:
        """Create a PIL Image of the final sticker template suitable for PDF print

        Args:
            label_data (dict): Dict with label data as stored in Editor widget class
            top_margin (float): Top margin of upper left sticker in mm
            left_margin (float): Left margin of upper left sticker in mm
            sticker_pattern (tuple): 2-Tuple with(rows, colums) representing sticker pattern
            sticker_width (float): Sticker width in mm
            sticker_height (float): Sticker height in mm
            horizontal_margin (float): Horizontal margin between stickers in mm
            vertical_margin (float): Vertical margin between stickers in mm

        Returns:
            Image: PIL Image suitable for print out
        """
        # Create a blank A4 page
        page = Image.new('RGBA', (self.a4_width_px, self.a4_height_px), (255, 255, 255, 255))

        # Convert dimensions to pixels
        top_margin_px = int(top_margin / 25.4 * self.dpi)
        left_margin_px = int(left_margin / 25.4 * self.dpi)
        sticker_width_px = int(sticker_width / 25.4 * self.dpi)
        sticker_height_px = int(sticker_height / 25.4 * self.dpi)
        horizontal_margin_px = int(horizontal_margin / 25.4 * self.dpi)
        vertical_margin_px = int(vertical_margin / 25.4 * self.dpi)

        # Arrange the labels on the page
        for row in range(sticker_pattern[0]):
            for col in range(sticker_pattern[1]):
                # Calculate position for each label
                x_position = left_margin_px + col * (sticker_width_px + horizontal_margin_px)
                y_position = top_margin_px + row * (sticker_height_px + vertical_margin_px)

                # Check if label data exists for this position
                if (row, col) in label_data and 'final_print' in label_data[(row, col)]:
                    label_image = label_data[(row, col)]['final_print']

                    # Resize the label to fit the sticker dimensions
                    label_image_resized = label_image.resize((sticker_width_px, sticker_height_px), Image.Resampling.LANCZOS)

                    # Paste the label onto the page
                    page.paste(label_image_resized, (x_position, y_position), mask=label_image_resized)

        return page

    def save_to_pdf(self, page_image:Image, output_path:str) -> None:
        """Save image as a PDF

        Args:
            page_image (Image): Input PIL Image
            output_path (str): Output path
        """
        page_image.convert('RGB').save(output_path, 'PDF', resolution=self.dpi)
