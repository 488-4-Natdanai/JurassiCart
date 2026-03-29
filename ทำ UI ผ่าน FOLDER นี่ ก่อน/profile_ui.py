import sys
import tempfile
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QStackedWidget,
    QDateEdit,
)
from PySide6.QtCore import Qt, Signal, QDate, QPoint
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPolygon


# ─────────────────────────────────────────────
# Arrow image — created after QApplication
# ─────────────────────────────────────────────
ARROW_PATH = ""

def init_arrow():
    global ARROW_PATH
    px = QPixmap(12, 8)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(QColor("#555555")))
    triangle = QPolygon([QPoint(0, 0), QPoint(12, 0), QPoint(6, 8)])
    p.drawPolygon(triangle)
    p.end()
    path = os.path.join(tempfile.gettempdir(), "jc_arrow.png").replace("\\", "/")
    px.save(path)
    ARROW_PATH = path


# ─────────────────────────────────────────────
# Style constants
# ─────────────────────────────────────────────
OVAL_BTN_GREEN = """
    QPushButton {{
        background: #2e7d32; color: white;
        border: none; border-radius: {r}px;
    }}
    QPushButton:hover   {{ background: #1b5e20; }}
    QPushButton:pressed {{ background: #388e3c; }}
"""

OVAL_BTN_OUTLINE = """
    QPushButton {{
        background: white; color: #333;
        border: 1px solid #aaa; border-radius: {r}px;
    }}
    QPushButton:hover {{ background: #f5f5f5; border-color: #888; }}
"""

OVAL_BTN_RED = """
    QPushButton {{
        background: #e53935; color: white;
        border: none; border-radius: {r}px;
    }}
    QPushButton:hover {{ background: #c62828; }}
"""

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }
    QLineEdit:focus { border: 1.5px solid #2e7d32; }
"""

def combo_style():
    return f"""
    QComboBox {{
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }}
    QComboBox:focus {{ border: 1.5px solid #2e7d32; }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px; border: none; background: transparent;
    }}
    QComboBox::down-arrow {{
        image: url({ARROW_PATH});
        width: 12px; height: 8px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid #ccc;
        selection-background-color: #c8e6c9;
    }}
"""

def date_style():
    return f"""
    QDateEdit {{
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }}
    QDateEdit:focus {{ border: 1.5px solid #2e7d32; }}
    QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px; border: none; background: transparent;
    }}
    QDateEdit::down-arrow {{
        image: url({ARROW_PATH});
        width: 12px; height: 8px;
    }}
"""


# ─────────────────────────────────────────────
# Helper: circular avatar pixmap
# ─────────────────────────────────────────────
def make_avatar_pixmap(size=120):
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QBrush(QColor("#bdbdbd")))
    p.setPen(Qt.NoPen)
    p.drawEllipse(0, 0, size, size)
    head_r = size // 5
    p.setBrush(QBrush(QColor("#9e9e9e")))
    p.drawEllipse(size // 2 - head_r, size // 5, head_r * 2, head_r * 2)
    body_w = int(size * 0.55)
    body_h = int(size * 0.35)
    p.drawEllipse((size - body_w) // 2, int(size * 0.52), body_w, body_h)
    p.end()
    return px


# ─────────────────────────────────────────────
# Tab Bar
# ─────────────────────────────────────────────
class TabBar(QWidget):
    tab_changed = Signal(int)

    def __init__(self, tabs, parent=None):
        super().__init__(parent)
        self.active = 0
        self._buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, name in enumerate(tabs):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(46)
            btn.setMinimumWidth(160)
            btn.clicked.connect(lambda _, idx=i: self._on_click(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        self._update_styles()

    def _on_click(self, idx):
        self.active = idx
        self._update_styles()
        self.tab_changed.emit(idx)

    def _update_styles(self):
        for i, btn in enumerate(self._buttons):
            if i == self.active:
                btn.setStyleSheet("""
                    QPushButton {
                        background: white; border: none;
                        color: #222; font-weight: 600; padding: 0 24px;
                    }
                """)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #e8e8e8; border: none;
                        color: #555; font-weight: 400; padding: 0 24px;
                    }
                    QPushButton:hover { background: #f0f0f0; color: #222; }
                """)
                btn.setChecked(False)


# ─────────────────────────────────────────────
# Page 0 — My Profile
# ─────────────────────────────────────────────
class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)
        label_width = 110

        # Username (read-only)
        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Username"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        username_lbl = QLabel("Jane Doe001")
        username_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        username_lbl.setStyleSheet("color:#333;")
        row.addWidget(username_lbl); row.addStretch()
        form_layout.addLayout(row)

        # Editable fields
        for label_text, placeholder in [
            ("Name",         "Enter your name"),
            ("Email",        "Enter your email"),
            ("Phone Number", "Enter phone number"),
        ]:
            row = QHBoxLayout(); row.setSpacing(12)
            lbl = QLabel(label_text); lbl.setFixedWidth(label_width)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
            row.addWidget(lbl)
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setFont(QFont("Segoe UI", 10))
            field.setFixedHeight(34); field.setMinimumWidth(260)
            field.setStyleSheet(INPUT_STYLE)
            row.addWidget(field); row.addStretch()
            form_layout.addLayout(row)

        # Gender
        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Gender"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        gender_cb = QComboBox()
        gender_cb.addItems(["Female", "Male", "Other"])
        gender_cb.setFont(QFont("Segoe UI", 10))
        gender_cb.setFixedHeight(34); gender_cb.setMinimumWidth(160)
        gender_cb.setStyleSheet(combo_style())
        row.addWidget(gender_cb); row.addStretch()
        form_layout.addLayout(row)

        # Date of birth
        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Date of birth"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(2001, 1, 1))
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setFont(QFont("Segoe UI", 10))
        date_edit.setFixedHeight(34); date_edit.setMinimumWidth(160)
        date_edit.setStyleSheet(date_style())
        row.addWidget(date_edit); row.addStretch()
        form_layout.addLayout(row)

        form_layout.addSpacing(10)

        # Save button
        save_row = QHBoxLayout()
        save_row.addSpacing(label_width + 12)
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(100, 38)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
        save_row.addWidget(save_btn); save_row.addStretch()
        form_layout.addLayout(save_row)
        form_layout.addStretch()

        root.addLayout(form_layout, stretch=3)

        # Avatar
        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        avatar_layout.setSpacing(14)
        avatar_lbl = QLabel()
        avatar_lbl.setPixmap(make_avatar_pixmap(120))
        avatar_lbl.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar_lbl)
        select_btn = QPushButton("Select Image")
        select_btn.setFixedSize(120, 34)
        select_btn.setFont(QFont("Segoe UI", 9))
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.setStyleSheet(OVAL_BTN_OUTLINE.format(r=17))
        avatar_layout.addWidget(select_btn, alignment=Qt.AlignHCenter)
        avatar_layout.addStretch()

        root.addLayout(avatar_layout, stretch=1)


# ─────────────────────────────────────────────
# Page 1 — Wallet
# ─────────────────────────────────────────────
class WalletPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        left = QVBoxLayout()
        left.setSpacing(10)

        for amount in [5_000_000, 10_000_000, 50_000_000,
                       100_000_000, 500_000_000, 1_000_000_000]:
            row = QHBoxLayout(); row.setSpacing(16)

            label_frame = QFrame()
            label_frame.setStyleSheet("QFrame { background: #e8e8e8; border-radius: 21px; }")
            label_frame.setFixedHeight(42); label_frame.setMinimumWidth(260)
            label_inner = QHBoxLayout(label_frame)
            label_inner.setContentsMargins(20, 0, 20, 0)
            lbl = QLabel(f"Add ${amount:,}")
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #222; background: transparent;")
            label_inner.addWidget(lbl)
            row.addWidget(label_frame)

            add_btn = QPushButton("Add funds")
            add_btn.setFixedSize(110, 38)
            add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            add_btn.setCursor(Qt.PointingHandCursor)
            add_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
            row.addWidget(add_btn); row.addStretch()
            left.addLayout(row)

        left.addStretch()
        root.addLayout(left, stretch=3)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop); right.setSpacing(6)
        t = QLabel("Wallet Balance")
        t.setFont(QFont("Segoe UI", 11)); t.setStyleSheet("color:#555;")
        right.addWidget(t)
        a = QLabel("$1,000,000,000")
        a.setFont(QFont("Segoe UI", 26, QFont.Bold))
        a.setStyleSheet("color:#2e7d32;")
        right.addWidget(a)
        right.addStretch()
        root.addLayout(right, stretch=2)


# ─────────────────────────────────────────────
# Page 2 — Change Password
# ─────────────────────────────────────────────
class ChangePasswordPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(0)

        label_width = 150

        def make_field(label_text):
            row = QHBoxLayout(); row.setSpacing(12)
            lbl = QLabel(label_text); lbl.setFixedWidth(label_width)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
            row.addWidget(lbl)
            field = QLineEdit()
            field.setEchoMode(QLineEdit.Password)
            field.setFont(QFont("Segoe UI", 10))
            field.setFixedHeight(34); field.setMinimumWidth(280)
            field.setStyleSheet(INPUT_STYLE)
            row.addWidget(field); row.addStretch()
            return row

        layout.addLayout(make_field("Current Password"))
        layout.addSpacing(30)
        layout.addLayout(make_field("New Password"))
        layout.addSpacing(14)
        layout.addLayout(make_field("Confirm Password"))
        layout.addSpacing(20)

        btn_row = QHBoxLayout()
        btn_row.addSpacing(label_width + 12)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setFixedSize(110, 38)
        confirm_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
        btn_row.addWidget(confirm_btn); btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()


# ─────────────────────────────────────────────
# Top Navigation Bar
# ─────────────────────────────────────────────
class NavBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("QWidget { background: #2e7d32; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 16, 0)
        layout.setSpacing(10)

        logo_lbl = QLabel("🦕 JurassiCart")
        logo_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_lbl.setStyleSheet("color: white; letter-spacing: 1px;")
        layout.addWidget(logo_lbl)
        layout.addSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("Search")
        search.setFixedHeight(36)
        search.setFont(QFont("Segoe UI", 10))
        search.setStyleSheet("""
            QLineEdit {
                background: white; border: none;
                border-radius: 5px; padding: 0 14px; color: #333;
            }
        """)
        layout.addWidget(search, stretch=1)

        for icon_text in ["⊲", "🛒", "👤"]:
            btn = QPushButton(icon_text)
            btn.setFixedSize(40, 40)
            btn.setFont(QFont("Segoe UI", 16))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background: transparent; color: white; border: none; }
                QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 20px; }
            """)
            layout.addWidget(btn)


# ─────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.resize(900, 580)
        self.setMinimumSize(800, 500)

        menubar = self.menuBar()
        menubar.setStyleSheet(
            "QMenuBar { background: #1a1a1a; color: white; }"
            "QMenuBar::item:selected { background: #333; }"
        )
        for name in ["Edit", "Navigation", "Store", "Account"]:
            menubar.addMenu(name)

        central = QWidget()
        central.setStyleSheet("background: #f0f0f0;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(NavBar())

        content = QWidget()
        content.setStyleSheet("background: #f0f0f0;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 24, 30, 24)

        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border-radius: 10px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 12, 0)
        top_row.setSpacing(0)

        self.tab_bar = TabBar(["My Profile", "Wallet", "Change Password"])
        self.tab_bar.tab_changed.connect(self._switch_tab)
        top_row.addWidget(self.tab_bar)

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(80, 32)
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(OVAL_BTN_RED.format(r=16))
        top_row.addWidget(logout_btn, alignment=Qt.AlignVCenter)
        card_layout.addLayout(top_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ddd;")
        card_layout.addWidget(line)

        self.stack = QStackedWidget()
        self.stack.addWidget(ProfilePage())
        self.stack.addWidget(WalletPage())
        self.stack.addWidget(ChangePasswordPage())
        card_layout.addWidget(self.stack)

        content_layout.addWidget(card)
        main_layout.addWidget(content, stretch=1)

    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    init_arrow()          # สร้าง arrow image หลัง QApplication พร้อม
    window = MainWindow()
    window.show()
    sys.exit(app.exec())