import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon
dir = os.path.dirname(os.path.abspath(__file__))

class cart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("THIS IS CART PAGE")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

class checkout(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("THIS IS CHECKOUT PAGE")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)