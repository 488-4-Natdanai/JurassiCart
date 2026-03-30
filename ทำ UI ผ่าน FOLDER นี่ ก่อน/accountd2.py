import sys, os, ctypes
import tempfile
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QStackedWidget,
    QDateEdit, QDialog, QCheckBox, QToolBar
)
from PySide6.QtCore import Qt, Signal, QDate, QPoint, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPolygon, QPen, QIcon, QAction, QFontDatabase
dir = os.path.dirname(os.path.abspath(__file__))
dino_logo   = os.path.join(dir, "resorces", "dino2.png")
juras_logo  = os.path.join(dir, "resorces", "JurassiLogo.png")
USER_AVATAR_PATH = os.path.join(dir, "resorces","dino2.png") 
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
# Helper: create simple icon with QPainter
# (Used for icons without provided images like 'back' and 'cart')
# ─────────────────────────────────────────────
def create_simple_icon(type, size=32, color="#ffffff"):
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(color), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)

    if type == "back":
        p.drawPolyline([QPoint(size * 0.7, size * 0.3),
                        QPoint(size * 0.3, size * 0.5),
                        QPoint(size * 0.7, size * 0.7)])
    elif type == "cart":
        p.drawRect(int(size * 0.2), int(size * 0.35), int(size * 0.6), int(size * 0.5))
        p.drawEllipse(int(size * 0.25), int(size * 0.85), 4, 4)
        p.drawEllipse(int(size * 0.65), int(size * 0.85), 4, 4)
        p.drawPolyline([QPoint(size * 0.2, size * 0.35),
                        QPoint(size * 0.1, size * 0.15),
                        QPoint(size * 0.3, size * 0.15)])

    p.end()
    return QIcon(px)


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

        for label_text, placeholder in [
            ("Name",         "Enter your name"),
            ("Email",        "Enter your email"),
            ("Phone Number", "Enter your phone number"),
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
        try:
            avatar_pixmap = QPixmap(USER_AVATAR_PATH).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if avatar_pixmap.isNull():
                print(f"Error: Could not load user avatar from {USER_AVATAR_PATH}")
                px = QPixmap(120, 120); px.fill(QColor("#ddd"))
                avatar_lbl.setPixmap(px)
            else:
                avatar_lbl.setPixmap(avatar_pixmap)
        except Exception as e:
            print(f"Error loading user avatar: {e}")
            px = QPixmap(120, 120); px.fill(QColor("#ddd"))
            avatar_lbl.setPixmap(px)

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
# Popup — Purchase Info
# ─────────────────────────────────────────────
class PurchaseDialog(QDialog):
    def __init__(self, amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Purchase info")
        self.resize(420, 320)
        self.setStyleSheet("background: #f7f7f7;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("PAYMENT")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #222;")
        layout.addWidget(title)

        # Method Label
        lbl_method = QLabel("Please select a payment method")
        lbl_method.setFont(QFont("Segoe UI", 9))
        lbl_method.setStyleSheet("color: #333;")
        layout.addWidget(lbl_method)

        # Combo Box
        self.combo = QComboBox()
        self.combo.addItems(["Promptpay", "Credit / Debit Card", "Bank Transfer"])
        self.combo.setFixedHeight(36)
        self.combo.setFont(QFont("Segoe UI", 10))
        self.combo.setStyleSheet(combo_style())
        layout.addWidget(self.combo)

        layout.addSpacing(10)

        # Line 1
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("color: #ccc;")
        layout.addWidget(line1)

        # Total
        total_layout = QHBoxLayout()
        lbl_total = QLabel("Total:")
        lbl_total.setFont(QFont("Segoe UI", 12))
        lbl_total.setStyleSheet("color: #222;")
        
        val_total = QLabel(f"${amount:,}")
        val_total.setFont(QFont("Segoe UI", 12))
        val_total.setStyleSheet("color: #222;")
        val_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        total_layout.addWidget(lbl_total)
        total_layout.addWidget(val_total)
        layout.addLayout(total_layout)

        # Line 2
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color: #ccc;")
        layout.addWidget(line2)

        layout.addSpacing(5)

        # Checkbox & Terms
        agree_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #555555;
                background-color: #ffffff;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2e7d32;
                background-color: #f5f5f5;
                image: url(check.png); 
            }
        """)
        self.checkbox.setCursor(Qt.PointingHandCursor)
        
        lbl_terms = QLabel("I agree to the terms of the <u>JurassiCart purchase agreement</u>")
        lbl_terms.setFont(QFont("Segoe UI", 9))
        lbl_terms.setStyleSheet("color: #222;")
        
        agree_layout.addWidget(self.checkbox)
        agree_layout.addWidget(lbl_terms)
        agree_layout.addStretch()
        layout.addLayout(agree_layout)

        layout.addSpacing(15)

        # Purchase Button
        btn_layout = QHBoxLayout()
        self.btn_purchase = QPushButton("Purchase")
        self.btn_purchase.setFixedSize(120, 38)
        self.btn_purchase.setFont(QFont("Segoe UI", 11))
        self.btn_purchase.setCursor(Qt.PointingHandCursor)
        
        self.btn_purchase.setEnabled(False) 
        self.btn_purchase.setStyleSheet("""
            QPushButton {
                background: white; color: #222;
                border: 1px solid #ddd; border-radius: 19px;
            }
            QPushButton:hover:enabled { background: #f0f0f0; border-color: #bbb; }
            QPushButton:disabled { color: #aaa; background: #e0e0e0; border: none; }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_purchase)
        layout.addLayout(btn_layout)
        layout.addStretch()

        # Connect Events
        self.checkbox.toggled.connect(self.btn_purchase.setEnabled)
        self.btn_purchase.clicked.connect(self.accept)

    def _on_check(self, state):
        self.btn_purchase.setEnabled(state == Qt.Checked)

# ─────────────────────────────────────────────
# Page 1 — Wallet
# ─────────────────────────────────────────────
class WalletPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")
        
        self.current_balance = 0 

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        left = QVBoxLayout()
        left.setSpacing(10)

        for amount in [5_000_000, 10_000_000, 50_000_000,
                       100_000_000, 500_000_000, 1_000_000_000]:
            row = QHBoxLayout()
            row.setSpacing(16)

            label_frame = QFrame()
            label_frame.setStyleSheet("QFrame { background: #e8e8e8; border-radius: 21px; }")
            label_frame.setFixedHeight(42)
            label_frame.setMinimumWidth(260)
            
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
            
            add_btn.clicked.connect(lambda checked=False, amt=amount: self._open_purchase_dialog(amt))
            
            row.addWidget(add_btn)
            row.addStretch()
            left.addLayout(row)

        left.addStretch()
        root.addLayout(left, stretch=3)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)
        right.setSpacing(6)
        
        t = QLabel("Wallet Balance")
        t.setFont(QFont("Segoe UI", 11))
        t.setStyleSheet("color:#555;")
        right.addWidget(t)
        
        self.balance_lbl = QLabel(f"${self.current_balance:,}")
        self.balance_lbl.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.balance_lbl.setStyleSheet("color:#2e7d32;")
        right.addWidget(self.balance_lbl)
        
        right.addStretch()
        root.addLayout(right, stretch=2)

    def _open_purchase_dialog(self, amount):
        dialog = PurchaseDialog(amount, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.current_balance += amount
            
            self.balance_lbl.setText(f"${self.current_balance:,}")
            
            print(f"Purchased Done: ${self.current_balance:,}")

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()
        
    def create_menu(self):

        #Edit menu
        edit_menu = self.menuBar().addMenu("Edit")

        gen = QAction("Quit", self)
        gen.triggered.connect(sys.exit)
        edit_menu.addAction(gen)

        #Navigation menu
        nav_menu = self.menuBar().addMenu("Navigation")

        go_back = QAction("Go back", self)
        go_back.triggered.connect(lambda : print("go back"))
        nav_menu.addAction(go_back)

        go_forward = QAction("Go forward", self)
        go_forward.triggered.connect(lambda : print("go forward"))
        nav_menu.addAction(go_forward)

        go_home = QAction("Home", self)
        go_home.triggered.connect(lambda : print("go home"))
        nav_menu.addAction(go_home)

        #Store menu
        store_menu = self.menuBar().addMenu("Store")

        create_store = QAction("Create store", self)
        create_store.triggered.connect(lambda : print("create store"))
        store_menu.addAction(create_store)

        stock = QAction("Stock", self)
        stock.triggered.connect(lambda : print("go stock"))
        store_menu.addAction(stock)

        add_stock = QAction("Add stock", self)
        add_stock.triggered.connect(lambda : print("go add_stock"))
        store_menu.addAction(add_stock)

        #Acc menu
        acc_menu = self.menuBar().addMenu("Account")

        myacc = QAction("My account", self)
        myacc.triggered.connect(lambda : print("create store"))
        acc_menu.addAction(myacc)

        cart = QAction("My Cart", self)
        cart.triggered.connect(lambda : print("go cart"))
        acc_menu.addAction(cart)
        
    def create_toolbar(self):
        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar{
            background:#0b7a12;
            spacing:10px;
            padding:8px;
        }
        """)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        # Icon buttons
        icon_style = """
            QPushButton {
                color: white; font-size: 40px;
                background: transparent; border: none; padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
                border-radius: 20px;
            }
        """
        # Logo
        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40,40))

        self.name_btn = QPushButton("JurassiCart")
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.name_btn.setFont(QFont(font_family, 12))
        self.name_btn.setStyleSheet("""
            QPushButton {
                color: white; font-size: 30px; font-weight: bold;
                background: transparent; border: none;
            }
            QPushButton:hover { color: #ccffcc; }
        """)

        # Search bar
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 20px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 10, 0)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                font-size: 14px;
            }
        """)

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(dir, "resorces","search.png")))
        search_icon.clicked.connect(lambda : print("Search"))
        search_icon.setStyleSheet("background: #999999;")
        search_icon.setFixedSize(44, 44)
        search_icon.setIconSize(QSize(24,24))
        search_icon.setStyleSheet("""
            QPushButton {
                color: white; font-size: 40px;
                background: transparent; border: none; padding: 5px;
            }
            QPushButton:hover {
                background-color: #999999;
                border-radius: 22px;
            }
        """)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        self.filter_btn  = QPushButton()
        self.filter_btn.setIcon(QIcon(os.path.join(dir, "resorces","filter.png")))
        self.filter_btn.setIconSize(QSize(24,24))
        self.cart_btn    = QPushButton()
        self.cart_btn.setIcon(QIcon(os.path.join(dir, "resorces","cart.png")))
        self.cart_btn.setIconSize(QSize(40,40))
        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(os.path.join(dir, "resorces","user.png")))
        self.profile_btn.setIconSize(QSize(40,40))

        for btn in [self.logo, self.filter_btn, self.cart_btn, self.profile_btn]:
            btn.setFixedSize(44, 44)
            btn.setStyleSheet(icon_style)

        self.filter_btn.clicked.connect(lambda: print("Filter"))
        self.cart_btn.clicked.connect(lambda: print("Cart"))
        self.profile_btn.clicked.connect(lambda: print("Profile"))

        layout.addWidget(self.logo)
        layout.addWidget(self.name_btn)
        layout.addWidget(search_container, stretch=1)
        layout.addWidget(self.filter_btn)
        layout.addWidget(self.cart_btn)
        layout.addWidget(self.profile_btn)

        container.setLayout(layout)
        toolbar.addWidget(container)

        self.addToolBar(Qt.TopToolBarArea, toolbar)
def main():
    myappid = "dme.jurassicart.app"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    sys.argv += ['-platform', 'windows:darkmode=1']
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(dino_logo))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()