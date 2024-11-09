from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QHBoxLayout, QFileDialog, QMessageBox

import ui

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
        self.__templates__ = [k for k,_ in ui.template_data.items()]
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
        
    def registerPreviewer(self, previewer:ui.PreviewWidget) -> None:
        self.__previewer__ = previewer
        self.selected_template(self.__templates__[0])
        
    def registerLogger(self, logger:ui.FooterWidget) -> None:
        self.__logger__ = logger
        
    def registerEditor(self, editor:ui.EditOptionsWidget) -> None:
        self.__editor__ = editor
        
    def selected_template(self, index:int) -> None:
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
        if self.project_path_display.text() in [None, ""]:
            QMessageBox.critical(self, "Build Failed", "Please select a project folder first.")
            return
        
        success = self.previewer.generate_pdf(project_path=self.project_path_display.text())
        if success:
            QMessageBox.information(self, "Build Successful", "PDF successfully created.")
        else:
            QMessageBox.critical(self, "Build Failed", "An error occurred while creating the PDF.")