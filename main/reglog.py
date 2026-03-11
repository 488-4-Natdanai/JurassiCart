import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon
dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")

class login(QWidget):
    switch_to_register = Signal()
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ------------------
        # LEFT SIDE (IMAGE)
        # ------------------
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pix = QPixmap(os.path.join(dir,"resorces","longneck.jpg"))  # เปลี่ยนรูปตรงนี้
        self.left.setPixmap(self.pix)
        

        # ------------------
        # RIGHT SIDE
        # ------------------
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")

        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        # Login Card
        card = QFrame()
        card.setFixedSize(450, 500)
        card.setStyleSheet("""
        QFrame{
            background:white;
            border-radius:10px;
        }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0,0,0,20)

        # Header
        header = QLabel("  Login")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        header.setFont(QFont(font_family, 12))
        header.setFixedHeight(60)
        header.setStyleSheet("""
        QLabel{
            background:#0b7a12;
            color:white;
            font-size:28px;
            border-top-left-radius:10px;
            border-top-right-radius:10px;
        }
        """)

        # Inputs
        form = QVBoxLayout()
        form.setContentsMargins(30,20,30,10)
        form.setSpacing(15)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        for box in [self.username, self.password]:
            box.setFixedHeight(45)
            box.setStyleSheet("""
            QLineEdit{
                border:1px solid #ccc;
                border-radius:15px;
                padding-left:10px;
                background:#f3f3f3;
            }
            """)

        login_btn = QPushButton("LOGIN")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
        QPushButton{
            background:#0b7a12;
            color:white;
            font-weight:bold;
            border-radius:8px;
        }
        QPushButton:hover{
            background:#0d9416;
        }
        """)

        signup = QLabel("Don't have an account? <a href='#'>REGISTER</a>")
        signup.setAlignment(Qt.AlignCenter)
        signup.setTextInteractionFlags(Qt.TextBrowserInteraction)
        signup.setOpenExternalLinks(False)
        signup.linkActivated.connect(lambda: self.switch_to_register.emit())

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(login_btn)
        form.addWidget(signup)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)

        right_layout.addWidget(card)

        main_layout.addWidget(self.left,3)
        main_layout.addWidget(right_container,2)

class register(QWidget):
    switch_to_login = Signal()
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ------------------
        # LEFT SIDE (IMAGE)
        # ------------------
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pix = QPixmap(os.path.join(dir,"resorces","reg.jpg"))  # เปลี่ยนรูปตรงนี้
        self.left.setPixmap(self.pix)
        

        # ------------------
        # RIGHT SIDE
        # ------------------
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")

        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        # Login Card
        card = QFrame()
        card.setFixedSize(450, 500)
        card.setStyleSheet("""
        QFrame{
            background:white;
            border-radius:10px;
        }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0,0,0,20)

        # Header
        header = QLabel("  Register")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        header.setFont(QFont(font_family, 12))
        header.setFixedHeight(60)
        header.setStyleSheet("""
        QLabel{
            background:#0b7a12;
            color:white;
            font-size:28px;
            border-top-left-radius:10px;
            border-top-right-radius:10px;
        }
        """)

        # Inputs
        form = QVBoxLayout()
        form.setContentsMargins(30,20,30,10)
        form.setSpacing(15)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm password")
        self.confirm.setEchoMode(QLineEdit.Password)

        for box in [self.username, self.password, self.confirm]:
            box.setFixedHeight(45)
            box.setStyleSheet("""
            QLineEdit{
                border:1px solid #ccc;
                border-radius:15px;
                padding-left:10px;
                background:#f3f3f3;
            }
            """)

        register_btn = QPushButton("REGISTER")
        register_btn.setFixedHeight(45)
        register_btn.setStyleSheet("""
        QPushButton{
            background:#0b7a12;
            color:white;
            font-weight:bold;
            border-radius:8px;
        }
        QPushButton:hover{
            background:#0d9416;
        }
        """)

        login = QLabel("Already have an account? <a href='#'>LOGIN</a>")
        login.setAlignment(Qt.AlignCenter)
        login.setTextInteractionFlags(Qt.TextBrowserInteraction)
        login.setOpenExternalLinks(False)
        login.linkActivated.connect(lambda: self.switch_to_login.emit())

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.confirm)
        form.addWidget(register_btn)
        form.addWidget(login)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)

        right_layout.addWidget(card)

        main_layout.addWidget(self.left,3)
        main_layout.addWidget(right_container,2)
    