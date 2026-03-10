import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon
dir = os.path.dirname(os.path.abspath(__file__))

class register(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("THIS IS REGISTER PAGE")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

class login(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("THIS IS LOGIN PAGE")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)