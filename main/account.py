import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,QGraphicsDropShadowEffect,
    QSpinBox,QPushButton, QDialog, QComboBox, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar, QCheckBox)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon, QColor
dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor


class account(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        # ======================
        # ROOT + BG
        # ======================
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        bg = QWidget()
        bg.setStyleSheet("background:#dcdcdc;")
        bg_layout = QVBoxLayout(bg)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setAlignment(Qt.AlignCenter)

        # ======================
        # CARD (responsive)
        # ======================
        card = QFrame()
        card.setMinimumWidth(800)
        card.setMaximumWidth(1100)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet("""
        QFrame {
            background:white;
            border-radius:12px;
        }
        QFrame > QWidget {
            background:transparent;
        }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        main = QVBoxLayout(card)
        main.setContentsMargins(30, 20, 30, 25)
        main.setSpacing(15)

        # ======================
        # COMMON STYLES
        # ======================
        BTN_GREEN = """
        QPushButton {
            background:#0b7a12;
            color:white;
            font-size: 20px;
            font-weight: bold;
            border-radius:20px;
            padding:6px 14px;
        }
        QPushButton:hover { background:#095d0e; }
        QPushButton:pressed { background:#063d09; }
        """

        INPUT_STYLE = """
        QLineEdit, QDateEdit {
            background:white;
            border:1px solid #bcbcbc;
            border-radius:18px;
            padding:5px 10px;
        }
        QLineEdit:hover, QDateEdit:hover {
            background:#f7f7f7;
        }
        QLineEdit:focus, QDateEdit:focus {
            border:1px solid #0b7a12;
        }
        """

        COMBO_STYLE = """
        QComboBox {
            background:white;
            border:1px solid #bcbcbc;
            border-radius:18px;
            padding:5px 10px;
        }
        QComboBox:hover { background:#f2f2f2; }

        QComboBox QAbstractItemView {
            background:white;
            selection-background-color:#0b7a12;
            selection-color:white;
            border-radius:10px;
        }
        """

        # ======================
        # TAB BAR
        # ======================
        tab_bar = QHBoxLayout()
        tab_bar.setSpacing(0)

        self.tabs = []

        def make_tab(text, i):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setFixedHeight(50)
            b.clicked.connect(lambda: self.switch_tab(i))
            b.setStyleSheet("""
                QPushButton {
                    background:white;
                    border:none;
                    padding:10px 30px;
                    font-size:18px;
                }
                QPushButton:checked {
                    background:#e0e0e0;
                    border-bottom:3px solid #0b7a12;
                }
            """)
            self.tabs.append(b)
            return b

        tab_bar.addWidget(make_tab("My Profile", 0))
        tab_bar.addWidget(make_tab("Wallet", 1))
        tab_bar.addWidget(make_tab("Change Password", 2))
        tab_bar.addStretch()

        logout = QPushButton("Logout")
        logout.setStyleSheet("""
            QPushButton {
                background:red;
                color:white;
                border-radius:6px;
                padding:6px 14px;
            }
            QPushButton:hover { background:#cc0000; }
        """)
        tab_bar.addWidget(logout)

        main.addLayout(tab_bar)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#ccc;")
        main.addWidget(line)

        # ======================
        # STACK
        # ======================
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        main.addWidget(self.stack)

        # ======================
        # PROFILE
        # ======================
        profile = QWidget()
        profile.setStyleSheet("background:transparent;")
        p_layout = QHBoxLayout(profile)
        p_layout.setSpacing(40)

        form = QFormLayout()
        form.setSpacing(18)

        def input_line():
            w = QLineEdit()
            w.setFixedHeight(36)
            w.setStyleSheet(INPUT_STYLE)
            return w

        form.addRow("Username", QLabel("Jane Doe001"))
        form.addRow("Name", input_line())
        form.addRow("Email", input_line())
        form.addRow("Phone Number", input_line())

        gender = QComboBox()
        gender.addItems(["Female", "Male"])
        gender.setFixedHeight(36)
        gender.setStyleSheet(COMBO_STYLE)
        form.addRow("Gender", gender)

        dob = QDateEdit()
        dob.setCalendarPopup(True)
        dob.setDate(QDate.currentDate())
        dob.setFixedHeight(36)
        dob.setStyleSheet(INPUT_STYLE)
        form.addRow("Date of birth", dob)

        save = QPushButton("Save")
        save.setFixedSize(140, 42)
        save.setStyleSheet(BTN_GREEN)

        left = QVBoxLayout()
        left.addLayout(form)
        left.addWidget(save)
        left.addStretch()

        right = QVBoxLayout()
        avatar = QLabel()
        avatar.setFixedSize(130,130)
        avatar.setStyleSheet("background:#bdbdbd; border-radius:65px;")

        select = QPushButton("Select Image")
        select.setStyleSheet("""
            QPushButton {
                background:white;
                border:1px solid #bcbcbc;
                border-radius:15px;
                padding:6px 15px;
            }
            QPushButton:hover { background:#eee; }
        """)

        right.addWidget(avatar, alignment=Qt.AlignCenter)
        right.addWidget(select, alignment=Qt.AlignCenter)
        right.addStretch()

        p_layout.addLayout(left, 3)
        p_layout.addLayout(right, 1)

        self.stack.addWidget(profile)

        # ======================
        # WALLET
        # ======================
        wallet = QWidget()
        wallet.setStyleSheet("background:transparent;")
        w_layout = QHBoxLayout(wallet)

        left = QVBoxLayout()

        def wallet_item(text):
            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background:white;
                    border-radius:18px;
                }
            """)
            lay = QHBoxLayout(box)
            lay.setContentsMargins(15, 10, 15, 10)

            label = QLabel(text)

            btn = QPushButton("Add funds")
            btn.setStyleSheet("""
            QPushButton {
                background:#0b7a12;
                color:white;
                border-radius:12px;
                padding:6px 16px;
            }
            QPushButton:hover { background:#095d0e; }
            QPushButton:pressed { background:#063d09; }
            """)
            btn.clicked.connect(self.open_dialog)

            lay.addWidget(label)
            lay.addStretch()
            lay.addWidget(btn)

            left.addWidget(box)

        for amt in ["$5,000,000", "$10,000,000", "$50,000,000",
                    "$100,000,000", "$500,000,000", "$1,000,000,000"]:
            wallet_item(f"Add {amt}")

        left.addStretch()

        right = QVBoxLayout()
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("color:#ccc;")

        balance_layout = QVBoxLayout()
        balance_layout.addWidget(QLabel("Wallet Balance"))

        money = QLabel("$1,000,000,000")
        money.setStyleSheet("font-size:32px; color:#0b7a12; font-weight:bold;")

        balance_layout.addWidget(money)
        balance_layout.addStretch()

        w_layout.addLayout(left, 2)
        w_layout.addWidget(divider)
        w_layout.addLayout(balance_layout, 1)

        self.stack.addWidget(wallet)

        # ======================
        # PASSWORD
        # ======================
        pw = QWidget()
        pw.setStyleSheet("background:transparent;")
        pw_layout = QFormLayout(pw)
        pw_layout.setSpacing(20)

        def pw_input():
            w = QLineEdit()
            w.setEchoMode(QLineEdit.Password)
            w.setFixedHeight(36)
            w.setStyleSheet(INPUT_STYLE)
            return w

        pw_layout.addRow("Current Password", pw_input())
        pw_layout.addRow("New Password", pw_input())
        pw_layout.addRow("Confirm Password", pw_input())

        confirm = QPushButton("Confirm")
        confirm.setFixedSize(150, 42)
        confirm.setStyleSheet(BTN_GREEN)

        pw_layout.addRow("", confirm)

        self.stack.addWidget(pw)

        self.tabs[0].setChecked(True)

        # ======================
        # FINAL WRAP
        # ======================
        bg_layout.addWidget(card)
        root.addWidget(bg)

    def switch_tab(self, i):
        self.stack.setCurrentIndex(i)
        for idx, t in enumerate(self.tabs):
            t.setChecked(idx == i)

    # ======================
    # DIALOG
    # ======================
    def open_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Purchase info")
        dlg.setFixedSize(340, 460)

        layout = QVBoxLayout(dlg)

        title = QLabel("PAYMENT")
        title.setStyleSheet("font-size:22px;")
        layout.addWidget(title)

        combo = QComboBox()
        combo.addItems(["Promptpay", "Credit Card"])
        combo.setStyleSheet("""
        QComboBox {
            background:white;
            border:1px solid #bcbcbc;
            border-radius:15px;
            padding:5px 10px;
        }
        QComboBox:hover { background:#f2f2f2; }

        QComboBox QAbstractItemView {
            background:white;
            selection-background-color:#0b7a12;
            selection-color:white;
            border-radius:10px;
        }""")
        layout.addWidget(combo)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        total = QHBoxLayout()
        total.addWidget(QLabel("Total:"))
        total.addStretch()
        total.addWidget(QLabel("$1,000,000,000"))
        layout.addLayout(total)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        layout.addWidget(line2)

        check = QCheckBox("I agree to the terms of the JurassiCart purchase agreement")
        layout.addWidget(check)

        layout.addStretch()

        buy = QPushButton("Purchase")
        buy.setStyleSheet("""
            QPushButton {
                background:#e0e0e0;
                border-radius:18px;
                padding:10px;
            }
            QPushButton:hover { background:#cfcfcf; }
        """)
        layout.addWidget(buy)

        dlg.exec()