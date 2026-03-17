import sys, os
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QSpinBox, QCheckBox,
    QPushButton, QDialog, QMessageBox, QScrollArea,
    QFrame, QSizePolicy, QToolBar
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon

dir = os.path.dirname(os.path.abspath(__file__))
dino_logo   = os.path.join(dir, "resorces", "dino2.png")
juras_logo  = os.path.join(dir, "resorces", "JurassiLogo.png")

# ─────────────────────────────────────────────
#  Sample cart data
# ─────────────────────────────────────────────
CART_ITEMS = [
    {"name": "Tyrannosaurus Rex",  "type": "Carnivore", "variant": "#2d7a2d", "price": 25_000_000, "qty": 1, "checked": True},
    {"name": "Phuwiangosaurus",    "type": "Herbivore", "variant": "#e8e800", "price": 50_000_000, "qty": 1, "checked": False},
]

# ─────────────────────────────────────────────
#  CartItemRow – one row in the cart
# ─────────────────────────────────────────────
class CartItemRow(QFrame):
    changed = Signal()

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.item = item
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            CartItemRow {
                background: #e8e8e8;
                border-radius: 10px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)

        # Checkbox
        self.chk = QCheckBox()
        self.chk.setChecked(self.item["checked"])
        self.chk.setFixedSize(24, 24)
        self.chk.setStyleSheet("QCheckBox::indicator { width:20px; height:20px; }")
        self.chk.stateChanged.connect(self._on_check)
        row.addWidget(self.chk, alignment=Qt.AlignVCenter)

        # Dino icon placeholder
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(60, 60)
        icon_lbl.setStyleSheet("background:#bbb; border-radius:8px;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        dino_px = QPixmap(os.path.join(dir, "resorces", "dino2.png"))
        if not dino_px.isNull():
            icon_lbl.setPixmap(dino_px.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setText("🦕")
            icon_lbl.setFont(QFont("Segoe UI", 22))
        row.addWidget(icon_lbl, alignment=Qt.AlignVCenter)

        # Name + type + variant
        info = QVBoxLayout()
        info.setSpacing(2)

        lbl_name = QLabel(self.item["name"])
        lbl_name.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_name.setStyleSheet("color:#111; background:transparent;")
        info.addWidget(lbl_name)

        lbl_type = QLabel(self.item["type"])
        lbl_type.setFont(QFont("Segoe UI", 9))
        lbl_type.setStyleSheet("color:#555; background:transparent;")
        info.addWidget(lbl_type)

        variant_row = QHBoxLayout()
        variant_row.setSpacing(6)
        variant_lbl = QLabel("Variant")
        variant_lbl.setFont(QFont("Segoe UI", 9))
        variant_lbl.setStyleSheet("color:#555; background:transparent;")
        variant_row.addWidget(variant_lbl)

        color_box = QLabel()
        color_box.setFixedSize(18, 18)
        color_box.setStyleSheet(f"background:{self.item['variant']}; border-radius:3px;")
        variant_row.addWidget(color_box)
        variant_row.addStretch()
        info.addLayout(variant_row)

        row.addLayout(info, stretch=1)

        # Price
        price_lbl = QLabel(f"${self.item['price']:,}")
        price_lbl.setFont(QFont("Segoe UI", 11))
        price_lbl.setStyleSheet("color:#111;")
        price_lbl.setFixedWidth(130)
        price_lbl.setAlignment(Qt.AlignCenter)
        row.addWidget(price_lbl)

        # Quantity spinner
        qty_frame = QFrame()
        qty_frame.setStyleSheet("QFrame{background:#d0d0d0; border-radius:14px;}")
        qty_frame.setFixedSize(100, 32)
        qty_layout = QHBoxLayout(qty_frame)
        qty_layout.setContentsMargins(8, 0, 8, 0)
        qty_layout.setSpacing(4)

        self.qty_lbl = QLabel(str(self.item["qty"]))
        self.qty_lbl.setAlignment(Qt.AlignCenter)
        self.qty_lbl.setFont(QFont("Segoe UI", 10))
        self.qty_lbl.setFixedWidth(24)

        btn_up = QPushButton("∧")
        btn_dn = QPushButton("∨")
        for b in [btn_up, btn_dn]:
            b.setFixedSize(20, 20)
            b.setStyleSheet("QPushButton{background:transparent;border:none;font-size:10px;color:#333;}"
                            "QPushButton:hover{color:#000;}")

        btn_up.clicked.connect(self._qty_up)
        btn_dn.clicked.connect(self._qty_dn)

        qty_layout.addWidget(self.qty_lbl)
        qty_layout.addWidget(btn_up)
        qty_layout.addWidget(btn_dn)
        row.addWidget(qty_frame, alignment=Qt.AlignVCenter)

        # Delete button
        btn_del = QPushButton("Delete")
        btn_del.setFixedSize(80, 32)
        btn_del.setStyleSheet("""
            QPushButton{background:#d0d0d0;border:none;border-radius:14px;
                        font-size:10pt;color:#111;}
            QPushButton:hover{background:#bbb;}
        """)
        btn_del.clicked.connect(self._on_delete)
        row.addWidget(btn_del, alignment=Qt.AlignVCenter)

    def _qty_up(self):
        self.item["qty"] += 1
        self.qty_lbl.setText(str(self.item["qty"]))
        self.changed.emit()

    def _qty_dn(self):
        if self.item["qty"] > 1:
            self.item["qty"] -= 1
            self.qty_lbl.setText(str(self.item["qty"]))
            self.changed.emit()

    def _on_check(self):
        self.item["checked"] = self.chk.isChecked()
        self.changed.emit()

    def _on_delete(self):
        self.setParent(None)
        self.deleteLater()
        self.changed.emit()

# ─────────────────────────────────────────────
#  CartPage
# ─────────────────────────────────────────────
class CartPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = CART_ITEMS
        self.rows: list[CartItemRow] = []
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#f0f0f0;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 0)
        outer.setSpacing(0)

        # White card
        card = QFrame()
        card.setStyleSheet("QFrame{background:#fff; border-radius:14px;}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Title
        title = QLabel("Cart")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color:#111;")
        card_layout.addWidget(title)

        # Column headers
        header = QHBoxLayout()
        header.setContentsMargins(16, 0, 16, 0)
        for text, stretch, width in [
            ("", 0, 44), ("Ordering", 1, 0), ("Price", 0, 130),
            ("Quantity", 0, 100), ("Action", 0, 80)
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet("color:#888;")
            lbl.setAlignment(Qt.AlignCenter)
            if width:
                lbl.setFixedWidth(width)
            header.addWidget(lbl, stretch=stretch)
        card_layout.addLayout(header)

        # Scroll area for rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(8)
        self.rows_layout.addStretch()

        for item in self.items:
            self._add_row(item)

        scroll.setWidget(self.rows_container)
        card_layout.addWidget(scroll, stretch=1)

        outer.addWidget(card, stretch=1)

        # Bottom bar
        bottom = QFrame()
        bottom.setFixedHeight(64)
        bottom.setStyleSheet("QFrame{background:#f0f0f0;}")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(30, 0, 0, 0)
        bottom_layout.setSpacing(16)

        self.chk_all = QCheckBox("Select all")
        self.chk_all.setFont(QFont("Segoe UI", 11))
        self.chk_all.setStyleSheet("QCheckBox::indicator{width:20px;height:20px;}")
        self.chk_all.stateChanged.connect(self._select_all)
        bottom_layout.addWidget(self.chk_all)

        bottom_layout.addStretch()

        self.lbl_total = QLabel()
        self.lbl_total.setFont(QFont("Segoe UI", 11))
        self.lbl_total.setStyleSheet("color:#111;")
        bottom_layout.addWidget(self.lbl_total)

        btn_order = QPushButton("Order")
        btn_order.setFixedSize(160, 64)
        btn_order.setFont(QFont("Segoe UI", 16, QFont.Bold))
        btn_order.setStyleSheet("""
            QPushButton{background:#0b7a12;border:none;border-radius:10px;color:white;}
            QPushButton:hover{background:#095e0e;}
        """)
        btn_order.clicked.connect(lambda: QMessageBox.information(self, "Order", "Order placed!"))
        bottom_layout.addWidget(btn_order)

        outer.addWidget(bottom)

        self._refresh_total()

    def _add_row(self, item):
        row = CartItemRow(item)
        row.changed.connect(self._refresh_total)
        idx = self.rows_layout.count() - 1
        self.rows_layout.insertWidget(idx, row)
        self.rows.append(row)

    def _refresh_total(self):
        checked = [r.item for r in self.rows if not r.isHidden() and r.item.get("checked")]
        total = sum(i["price"] * i["qty"] for i in checked)
        count = sum(i["qty"] for i in checked)
        self.lbl_total.setText(f"Total({count} item{'s' if count != 1 else ''}): ${total:,}")

    def _select_all(self, state):
        for row in self.rows:
            row.chk.setChecked(bool(state))

# ─────────────────────────────────────────────
#  MainWindow
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()

        self.setCentralWidget(CartPage())

    def create_menu(self):
        edit_menu = self.menuBar().addMenu("Edit")
        gen = QAction("Quit", self)
        gen.triggered.connect(sys.exit)
        edit_menu.addAction(gen)

        nav_menu = self.menuBar().addMenu("Navigation")
        for label, slot in [("Go back", lambda: print("go back")),
                             ("Go forward", lambda: print("go forward")),
                             ("Home", lambda: print("go home"))]:
            a = QAction(label, self)
            a.triggered.connect(slot)
            nav_menu.addAction(a)

        store_menu = self.menuBar().addMenu("Store")
        for label, slot in [("Create store", lambda: print("create store")),
                             ("Stock", lambda: print("go stock")),
                             ("Add stock", lambda: print("go add_stock"))]:
            a = QAction(label, self)
            a.triggered.connect(slot)
            store_menu.addAction(a)

        acc_menu = self.menuBar().addMenu("Account")
        for label, slot in [("My account", lambda: print("my account")),
                             ("My Cart", lambda: print("go cart"))]:
            a = QAction(label, self)
            a.triggered.connect(slot)
            acc_menu.addAction(a)

    def create_toolbar(self):
        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar{background:#0b7a12;spacing:10px;padding:8px;}")

        container = QWidget()
        container.setStyleSheet("QWidget { background: #0b7a12; }")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        icon_style = (
            "QPushButton { color: white; background: transparent; border: none; padding: 5px; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.2); border-radius: 22px; }"
        )

        # Logo
        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40, 40))
        self.logo.setFixedSize(44, 44)
        self.logo.setStyleSheet(icon_style)

        # Name with custom font
        font_path = os.path.join(dir, "resorces", "DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        name_font = QFont(families[0], 18) if families else QFont("Segoe UI", 18, QFont.Bold)

        self.name_btn = QPushButton("JurassiCart")
        self.name_btn.setFont(name_font)
        self.name_btn.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; }"
            "QPushButton:hover { color: #ccffcc; }"
        )

        # Search bar
        search_container = QWidget()
        search_container.setStyleSheet("QWidget{background:white;border-radius:20px;}")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 10, 0)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet("QLineEdit{border:none;background:transparent;font-size:14px;color:#333;}")

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(dir, "resorces", "search.png")))
        search_icon.setFixedSize(36, 36)
        search_icon.setIconSize(QSize(22, 22))
        search_icon.setStyleSheet("""
            QPushButton{background:transparent;border:none;}
            QPushButton:hover{background-color:#ddd;border-radius:18px;}
        """)
        search_icon.clicked.connect(lambda: print("Search"))

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        # Right buttons — set icon + style individually (no loop override)
        self.filter_btn = QPushButton()
        self.filter_btn.setIcon(QIcon(os.path.join(dir, "resorces", "filter.png")))
        self.filter_btn.setIconSize(QSize(28, 28))
        self.filter_btn.setFixedSize(44, 44)
        self.filter_btn.setStyleSheet(icon_style)
        self.filter_btn.clicked.connect(lambda: print("Filter"))

        self.cart_btn = QPushButton()
        self.cart_btn.setIcon(QIcon(os.path.join(dir, "resorces", "cart.png")))
        self.cart_btn.setIconSize(QSize(36, 36))
        self.cart_btn.setFixedSize(44, 44)
        self.cart_btn.setStyleSheet(icon_style)
        self.cart_btn.clicked.connect(lambda: print("Cart"))

        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(os.path.join(dir, "resorces", "user.png")))
        self.profile_btn.setIconSize(QSize(36, 36))
        self.profile_btn.setFixedSize(44, 44)
        self.profile_btn.setStyleSheet(icon_style)
        self.profile_btn.clicked.connect(lambda: print("Profile"))

        self.filter_btn.clicked.connect(lambda: print("Filter"))
        self.cart_btn.clicked.connect(lambda: print("Cart"))
        self.profile_btn.clicked.connect(lambda: print("Profile"))

        layout.addWidget(self.logo)
        layout.addWidget(self.name_btn)
        layout.addWidget(search_container, stretch=1)
        layout.addWidget(self.filter_btn)
        layout.addWidget(self.cart_btn)
        layout.addWidget(self.profile_btn)

        toolbar.addWidget(container)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    
# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
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
