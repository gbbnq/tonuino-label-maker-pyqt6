from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout

from time import gmtime, strftime

class FooterWidget(QWidget):
    def __init__(self):
        super(FooterWidget, self).__init__()
        layout = QVBoxLayout()

        # Log window
        self.log_window = QTextEdit()
        self.log_window.setStyleSheet("background-color: black; color: white; font-family: Sans-Serif;")
        self.log_window.setReadOnly(True)

        layout.addWidget(self.log_window)
        self.setLayout(layout)
        
    def log(self, message:str):
        self.log_window.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " - " + message)
        