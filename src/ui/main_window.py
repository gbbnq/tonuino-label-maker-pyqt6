from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from ui import HeaderWidget
from ui import PreviewWidget
from ui import EditOptionsWidget
from ui import FooterWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Tonuino Cover Maker")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        self.layout = QVBoxLayout()

        # Footer for logs
        self.footer = FooterWidget()
        self.footer.setFixedHeight(100)
        
        # Main area
        self.main_area = QWidget()
        self.main_area_layout = QHBoxLayout()
        
        # Preview widget for page
        self.preview = PreviewWidget()
        self.preview.setFixedWidth(300)
        
        # Label editor
        self.edit_options = EditOptionsWidget()
        
        self.main_area_layout.addWidget(self.preview)
        self.main_area_layout.addWidget(self.edit_options)
        self.main_area.setLayout(self.main_area_layout)
        
        # Header
        self.header = HeaderWidget()
        
        # Register components
        self.header.registerEditor(self.edit_options)
        self.header.registerPreviewer(self.preview)
        self.header.registerLogger(self.footer)
        self.preview.registerLogger(self.footer)
        self.edit_options.registerLogger(self.footer)
        self.edit_options.registerPreviewer(self.preview)
        self.preview.registerEditor(self.edit_options)

        # Add components to layout
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.main_area)
        self.layout.addWidget(self.footer)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)