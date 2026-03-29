import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QFileDialog, QSizePolicy,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QColor, QPainterPath

dir_path = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────── helpers ────────────────────────────

GREEN        = "#0b7a12"
GREEN_HOVER  = "#0a6610"
LIGHT_GRAY   = "#f5f5f5"
TAB_ACTIVE   = "#ffffff"
TAB_INACTIVE = "#e0e0e0"

BTN_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: white;
        border: none;
        border-radius: 18px;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 28px;
    }}
    QPushButton:hover {{
        background-color: {hover};
    }}
    QPushButton:pressed {{
        background-color: #085c0e;
    }}
"""

INPUT_STYLE = """
    QLineEdit, QComboBox {
        border: 1px solid #cccccc;
        border-radius: 14px;
        padding: 5px 14px;
        font-size: 13px;
        background: white;
        min-width: 200px;
        min-height: 28px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1.5px solid #0b7a12;
    }
    QComboBox::drop-down { border: none; width: 24px; }
    QComboBox::down-arrow { width: 12px; height: 12px; }
"""

LABEL_STYLE = "font-size: 13px; color: #333333;"


def make_tab_btn(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCheckable(True)
    btn.setMinimumWidth(130)
    btn.setMinimumHeight(42)
    btn.setFont(QFont("Segoe UI", 11))
    return btn


def apply_tab_styles(buttons: list, active_index: int):
    for i, btn in enumerate(buttons):
        if i == active_index:
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    border-radius: 0px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 8px 20px;
                }
            """)
            btn.setChecked(True)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: #e8e8e8;
                    border: 1px solid #cccccc;
                    border-radius: 0px;
                    font-size: 13px;
                    color: #555555;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background: #d8d8d8;
                }
            """)
            btn.setChecked(False)


# ──────────────────────── sub-pages ─────────────────────────────

class MyProfilePage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        # ── left: form ──
        form_widget = QWidget()
        form = QGridLayout(form_widget)
        form.setVerticalSpacing(16)
        form.setHorizontalSpacing(16)
        form.setColumnStretch(1, 1)

        fields = [
            ("Username",     "Jane Doe001",     False, "lineedit"),
            ("Name",         "Jane Doe",        True,  "lineedit"),
            ("Email",        "Jane.d@email.com",True,  "lineedit"),
            ("Phone Number", "09x-xxx-xxxx",    True,  "lineedit"),
            ("Gender",       ["Female","Male","Other"], True, "combo"),
            ("Date of birth","1/01/01",         True,  "combo"),
        ]

        self.inputs = {}
        for row, (lbl_text, value, editable, kind) in enumerate(fields):
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(LABEL_STYLE)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            form.addWidget(lbl, row, 0)

            if kind == "lineedit":
                inp = QLineEdit(value if isinstance(value, str) else "")
                inp.setReadOnly(not editable)
                inp.setStyleSheet(INPUT_STYLE)
                if not editable:
                    inp.setStyleSheet(INPUT_STYLE + "QLineEdit{background:#f0f0f0; color:#666;}")
                form.addWidget(inp, row, 1)
                self.inputs[lbl_text] = inp
            else:
                cb = QComboBox()
                if isinstance(value, list):
                    cb.addItems(value)
                else:
                    cb.addItem(value)
                cb.setStyleSheet(INPUT_STYLE)
                form.addWidget(cb, row, 1)
                self.inputs[lbl_text] = cb

        # save button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BTN_STYLE.format(bg=GREEN, hover=GREEN_HOVER))
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(lambda: print("Save profile"))
        form.addWidget(save_btn, len(fields), 1, alignment=Qt.AlignLeft)

        root.addWidget(form_widget, stretch=2)

        # ── right: avatar ──
        avatar_widget = QWidget()
        avatar_layout = QVBoxLayout(avatar_widget)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(12)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(110, 110)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: #b0b0b0;
                border-radius: 55px;
            }
        """)
        # default user icon text
        self.avatar_label.setText("👤")
        self.avatar_label.setFont(QFont("Segoe UI Emoji", 40))
        self.avatar_label.setAlignment(Qt.AlignCenter)

        select_btn = QPushButton("Select Image")
        select_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #aaaaaa;
                border-radius: 12px;
                font-size: 12px;
                padding: 5px 16px;
                color: #333;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        select_btn.clicked.connect(self._select_image)

        avatar_layout.addStretch()
        avatar_layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        avatar_layout.addWidget(select_btn, alignment=Qt.AlignCenter)
        avatar_layout.addStretch()

        root.addWidget(avatar_widget, stretch=1)

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            pix = QPixmap(path).scaled(110, 110, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.avatar_label.setText("")
            self.avatar_label.setPixmap(pix)


class WalletPage(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 1_000_000_000
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(40)

        # ── left: fund options ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        amounts = [5_000_000, 10_000_000, 50_000_000,
                   100_000_000, 500_000_000, 1_000_000_000]

        for amt in amounts:
            row = QWidget()
            row.setFixedHeight(44)
            row.setStyleSheet("""
                QWidget {
                    background: white;
                    border: 1px solid #dddddd;
                    border-radius: 8px;
                }
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 4, 14, 4)

            lbl = QLabel(f"Add ${amt:,.0f}")
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet("border:none; background:transparent;")

            add_btn = QPushButton("Add funds")
            add_btn.setFixedWidth(100)
            add_btn.setFixedHeight(30)
            add_btn.setStyleSheet(BTN_STYLE.format(bg=GREEN, hover=GREEN_HOVER))
            add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            add_btn.clicked.connect(lambda checked, a=amt: self._add_funds(a))

            row_layout.addWidget(lbl)
            row_layout.addStretch()
            row_layout.addWidget(add_btn)

            left_layout.addWidget(row)

        left_layout.addStretch()
        root.addWidget(left, stretch=3)

        # ── right: balance ──
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_layout.setContentsMargins(10, 10, 0, 0)
        right_layout.setSpacing(6)

        bal_title = QLabel("Wallet Balance")
        bal_title.setFont(QFont("Segoe UI", 11))
        bal_title.setStyleSheet("color: #555555;")

        self.balance_label = QLabel(f"${self.balance:,.0f}")
        self.balance_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.balance_label.setStyleSheet(f"color: {GREEN};")
        self.balance_label.setWordWrap(True)

        right_layout.addWidget(bal_title)
        right_layout.addWidget(self.balance_label)
        root.addWidget(right, stretch=2)

    def _add_funds(self, amount: int):
        self.balance += amount
        self.balance_label.setText(f"${self.balance:,.0f}")


class ChangePasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(50, 40, 50, 30)
        root.setSpacing(20)

        form_widget = QWidget()
        form = QGridLayout(form_widget)
        form.setVerticalSpacing(18)
        form.setHorizontalSpacing(16)
        form.setColumnStretch(1, 1)

        fields = [
            ("Current Password", True),
            ("", False),          # spacer row
            ("New Password", False),
            ("Confirm Password", False),
        ]

        self.pw_inputs = {}
        real_row = 0
        for lbl_text in ["Current Password", "New Password", "Confirm Password"]:
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(LABEL_STYLE)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            inp = QLineEdit()
            inp.setEchoMode(QLineEdit.Password)
            inp.setStyleSheet(INPUT_STYLE)
            inp.setMinimumWidth(220)

            if lbl_text == "Current Password":
                form.addWidget(lbl, 0, 0)
                form.addWidget(inp, 0, 1)
                # spacer
                spacer = QLabel("")
                spacer.setFixedHeight(10)
                form.addWidget(spacer, 1, 0, 1, 2)
                real_row = 2
            else:
                form.addWidget(lbl, real_row, 0)
                form.addWidget(inp, real_row, 1)
                real_row += 1

            self.pw_inputs[lbl_text] = inp

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setStyleSheet(BTN_STYLE.format(bg=GREEN, hover=GREEN_HOVER))
        confirm_btn.setFixedWidth(130)
        confirm_btn.clicked.connect(self._confirm)
        form.addWidget(confirm_btn, real_row + 1, 1, alignment=Qt.AlignLeft)

        root.addWidget(form_widget)
        root.addStretch()

    def _confirm(self):
        cur  = self.pw_inputs["Current Password"].text()
        new  = self.pw_inputs["New Password"].text()
        conf = self.pw_inputs["Confirm Password"].text()
        if new != conf:
            print("Passwords do not match!")
        else:
            print(f"Password change confirmed (current={cur})")


# ──────────────────────── main widget ───────────────────────────

class AccountPage(QWidget):
    """
    Drop-in replacement for setCentralWidget().
    Contains: My Profile | Wallet | Change Password tabs + Logout button.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.setSpacing(0)

        # ── card container ──
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── tab bar ──
        tab_bar = QWidget()
        tab_bar.setStyleSheet("background: transparent;")
        tab_bar_layout = QHBoxLayout(tab_bar)
        tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        tab_bar_layout.setSpacing(0)

        self.tab_profile  = make_tab_btn("My Profile")
        self.tab_wallet   = make_tab_btn("Wallet")
        self.tab_password = make_tab_btn("Change Password")

        self.tabs = [self.tab_profile, self.tab_wallet, self.tab_password]

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 16px;
            }
            QPushButton:hover { background: #c62828; }
        """)
        logout_btn.setFixedHeight(32)
        logout_btn.clicked.connect(lambda: print("Logout"))

        tab_bar_layout.addWidget(self.tab_profile)
        tab_bar_layout.addWidget(self.tab_wallet)
        tab_bar_layout.addWidget(self.tab_password)
        tab_bar_layout.addStretch()
        tab_bar_layout.addWidget(logout_btn)
        tab_bar_layout.setContentsMargins(0, 0, 8, 0)

        # ── separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #cccccc;")

        # ── stacked pages ──
        from PySide6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget()
        self.page_profile  = MyProfilePage()
        self.page_wallet   = WalletPage()
        self.page_password = ChangePasswordPage()
        self.stack.addWidget(self.page_profile)
        self.stack.addWidget(self.page_wallet)
        self.stack.addWidget(self.page_password)

        card_layout.addWidget(tab_bar)
        card_layout.addWidget(sep)
        card_layout.addWidget(self.stack)

        outer.addWidget(card)

        # ── connect tabs ──
        self.tab_profile.clicked.connect(lambda: self._switch(0))
        self.tab_wallet.clicked.connect(lambda: self._switch(1))
        self.tab_password.clicked.connect(lambda: self._switch(2))

        self._switch(0)

    def _switch(self, index: int):
        self.stack.setCurrentIndex(index)
        apply_tab_styles(self.tabs, index)