import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon

import database as db

dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")

class login(QWidget):
    switch_to_register = Signal()
    login_success = Signal(dict)   # emits user dict on successful login

    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):
        """Build the login form layout with image, username/password fields, and login button."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # LEFT SIDE (image)
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left.setPixmap(QPixmap(os.path.join(dir, "resorces", "longneck.jpg")))

        # RIGHT SIDE
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(450, 500)
        card.setStyleSheet("QFrame{background:white;border-radius:10px;}")
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
            QLabel{background:#0b7a12;color:white;font-size:28px;
                   border-top-left-radius:10px;border-top-right-radius:10px;}
        """)

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
                QLineEdit{border:1px solid #ccc;border-radius:15px;
                          padding-left:10px;background:#f3f3f3;}
            """)

        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setStyleSheet("color:#cc0000; font-size:9pt;")
        self.error_lbl.setVisible(False)

        login_btn = QPushButton("LOGIN")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
            QPushButton{background:#0b7a12;color:white;font-weight:bold;border-radius:8px;}
            QPushButton:hover{background:#0d9416;}
        """)
        login_btn.clicked.connect(self._on_login)
        self.password.returnPressed.connect(self._on_login)

        signup = QLabel("Don't have an account? <a href='#'>REGISTER</a>")
        signup.setAlignment(Qt.AlignCenter)
        signup.setTextInteractionFlags(Qt.TextBrowserInteraction)
        signup.setOpenExternalLinks(False)
        signup.linkActivated.connect(lambda: self.switch_to_register.emit())

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.error_lbl)
        form.addWidget(login_btn)
        form.addWidget(signup)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)
        right_layout.addWidget(card)

        main_layout.addWidget(self.left, 3)
        main_layout.addWidget(right_container, 2)

    def _on_login(self):
        """Validate credentials and emit login_success or show an error message."""
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            self._show_error("Please enter username and password.")
            return

        # เช็คก่อนว่า username มีใน DB ไหม
        all_users = db._read(db.USERS_CSV)
        exists = any(u["username"].lower() == username.lower() for u in all_users)
        if not exists:
            reply = QMessageBox.question(
                self, "Account not found",
                f"No account found for \"{username}\".\nWould you like to register?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.switch_to_register.emit()
            return

        user = db.login_user(username, password)
        if user:
            self.error_lbl.setVisible(False)
            self.username.clear()
            self.password.clear()
            self.login_success.emit(user)
        else:
            self._show_error("Incorrect password. Please try again.")

    def _show_error(self, msg: str):
        """Display an error message in the login form."""
        self.error_lbl.setText(msg)
        self.error_lbl.setVisible(True)

class register(QWidget):
    switch_to_login = Signal()
    register_success = Signal(dict)   # emits user dict on successful register

    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):
        """Build the registration form layout with image, input fields, and register button."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # LEFT SIDE (IMAGE)
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left.setPixmap(QPixmap(os.path.join(dir,"resorces","reg.jpg")))

        # RIGHT SIDE
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(450, 540)
        card.setStyleSheet("QFrame{background:white;border-radius:10px;}")
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
            QLabel{background:#0b7a12;color:white;font-size:28px;
                   border-top-left-radius:10px;border-top-right-radius:10px;}
        """)

        form = QVBoxLayout()
        form.setContentsMargins(30,20,30,10)
        form.setSpacing(12)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email (optional)")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm password")
        self.confirm.setEchoMode(QLineEdit.Password)

        for box in [self.username, self.email, self.password, self.confirm]:
            box.setFixedHeight(45)
            box.setStyleSheet("""
                QLineEdit{border:1px solid #ccc;border-radius:15px;
                          padding-left:10px;background:#f3f3f3;}
            """)

        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setStyleSheet("color:#cc0000; font-size:9pt;")
        self.error_lbl.setVisible(False)

        register_btn = QPushButton("REGISTER")
        register_btn.setFixedHeight(45)
        register_btn.setStyleSheet("""
            QPushButton{background:#0b7a12;color:white;font-weight:bold;border-radius:8px;}
            QPushButton:hover{background:#0d9416;}
        """)
        register_btn.clicked.connect(self._on_register)

        login_lbl = QLabel("Already have an account? <a href='#'>LOGIN</a>")
        login_lbl.setAlignment(Qt.AlignCenter)
        login_lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
        login_lbl.setOpenExternalLinks(False)
        login_lbl.linkActivated.connect(lambda: self.switch_to_login.emit())

        form.addWidget(self.username)
        form.addWidget(self.email)
        form.addWidget(self.password)
        form.addWidget(self.confirm)
        form.addWidget(self.error_lbl)
        form.addWidget(register_btn)
        form.addWidget(login_lbl)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)
        right_layout.addWidget(card)

        main_layout.addWidget(self.left, 3)
        main_layout.addWidget(right_container, 2)

    def _on_register(self):
        """Validate registration inputs, create the account, and redirect to login."""
        username = self.username.text().strip()
        email    = self.email.text().strip()
        password = self.password.text()
        confirm  = self.confirm.text()

        if not username or not password:
            self._show_error("Username and password are required.")
            return
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return
        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        user = db.register_user(username, password, email)
        if user is None:
            self._show_error("Username already taken.")
            return

        # clear form
        self.username.clear()
        self.email.clear()
        self.password.clear()
        self.confirm.clear()
        self.error_lbl.setVisible(False)

        QMessageBox.information(
            self, "Registration Successful",
            f"Account \"{username}\" created!\nPlease log in."
        )
        self.switch_to_login.emit()   # กลับไปหน้า login

    def _show_error(self, msg: str):
        """Display an error message in the registration form."""
        self.error_lbl.setText(msg)
        self.error_lbl.setVisible(True)