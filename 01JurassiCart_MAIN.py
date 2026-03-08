import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)

def main():
    sys.argv += ['-platform', 'windows:darkmode=1']
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()