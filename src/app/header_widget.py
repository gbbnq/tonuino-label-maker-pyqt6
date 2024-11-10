from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QHBoxLayout, QFileDialog, QMessageBox

import os
import app

from .pdf_generator import PDFCreator

class HeaderWidget(QWidget):
    def __init__(self):
        super(HeaderWidget, self).__init__()
        
        # Private attributes
        self.__previewer__ = None
        self.__editor__ = None
        self.__logger__ = None
        self.__templates__ = [None]

        # Button for project path
        self.project_path_btn = QPushButton("Select Export Path")
        self.project_path_btn.clicked.connect(self.select_project_path)
        
        self.project_path_display = QLineEdit()
        self.project_path_display.setReadOnly(True)

        # Label template dropdown
        self.label_template_dropdown = QComboBox()
        self.__templates__ = [k for k,_ in app.template_data.items()]
        self.label_template_dropdown.addItems(self.__templates__)
        self.label_template_dropdown.currentTextChanged.connect(self.selected_template)

        # Build button
        self.build_button = QPushButton("Export PDF")
        self.build_button.clicked.connect(self.build_project)

        # Add widgets to layout
        layout = QHBoxLayout()
        layout.addWidget(self.project_path_btn)
        layout.addWidget(self.project_path_display)
        layout.addWidget(self.label_template_dropdown)
        layout.addWidget(self.build_button)
        self.setLayout(layout)
        
    def registerPreviewer(self, previewer:app.PreviewWidget) -> None:
        """Register the preview widget

        Args:
            logger (ui.PreviewWidget): Instance of preview widget class
        """
        self.__previewer__ = previewer
        self.selected_template(self.__templates__[0])
        
    def registerLogger(self, logger:app.FooterWidget) -> None:
        """Register the logger widget

        Args:
            logger (ui.FooterWidget): Instance of logger widget class
        """
        self.__logger__ = logger
        
    def registerEditor(self, editor:app.EditOptionsWidget) -> None:
        """Register the editor widget

        Args:
            editor (ui.EditOptionsWidget): Instance of editor widget class
        """
        self.__editor__ = editor
        
    def selected_template(self, index:int) -> None:
        """Update template previewer and editor widgets

        Args:
            index (int): Id of template
        """
        if self.__logger__:
            self.__logger__.log("New template selected. Clearing label data.")
        self.__previewer__.select_template(index)
        self.__editor__.select_template(index)
        
    def select_project_path(self):
        """Open a dialog for selecting project path
        """
        dialog = QFileDialog(self, "Select Project Folder")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        if dialog.exec():
            project_path = dialog.selectedFiles()[0]
            self.project_path_display.setText(project_path)

    def build_project(self) -> None:
        """Generate PDF
        """
        if self.project_path_display.text() in [None, ""]:
            QMessageBox.critical(self, "Build Failed", "Please select a project folder first.")
            return
        
        try:
            pdf = PDFCreator(dpi=300)
            image = pdf.create_label_page(
                label_data=self.__editor__.label_data,
                top_margin=self.__editor__.config['top_margin'],
                left_margin=self.__editor__.config['left_margin'],
                sticker_pattern=self.__editor__.config['sticker_pattern'],
                sticker_width=self.__editor__.config['sticker_width'],
                sticker_height=self.__editor__.config['sticker_height'],
                horizontal_margin=self.__editor__.config['horizontal_margin'],
                vertical_margin=self.__editor__.config['vertical_margin'],
            )
            pdf_path = os.path.join(self.project_path_display.text(), "output.pdf")
            pdf.save_to_pdf(image, pdf_path)
            success = True
        except Exception as e:
            if self.__logger__:
                self.__logger__.log(f"PDF Generation failed with error: {e}")
            success = False
        
        if success:
            QMessageBox.information(self, "Build Successful", "PDF successfully created.")
        else:
            QMessageBox.critical(self, "Build Failed", "An error occurred while creating the PDF.")