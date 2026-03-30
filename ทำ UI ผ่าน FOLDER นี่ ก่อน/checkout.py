import sys, os
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame,
    QSizePolicy, QToolBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon

dir = os.path.dirname(os.path.abspath(__file__))
dino_logo  = os.path.join(dir, "resorces", "dino2.png")
juras_logo = os.path.join(dir, "resorces", "JurassiLogo.png")

# ── shared cart data (same reference as cart.py would use) ──────────────────
CART_ITEMS = [
    {"name": "Tyrannosaurus Rex", "type": "Carnivore", "variant": "#2d7a2d", "price": 25_000_000, "qty": 1, "checked": True},
    {"name": "Phuwiangosaurus",   "type": "Herbivore", "variant": "#e8e800", "price": 50_000_000, "qty": 1, "checked": False},
]

# ── mock wallet balance ──────────────────────────────────────────────────────
WALLET_BALANCE = 30_000_000   # change to test insufficient-fund path


# ────────────────────────────────────────────────────────────────────────────
#  OrderSummaryItem  – one card in the right panel
# ────────────────────────────────────────────────────────────────────────────
class OrderSummaryItem(QFrame):
    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame{background:#f7f7f7; border-radius:10px;}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 10, 10, 10)
        row.setSpacing(12)

        # dino thumbnail
        icon = QLabel()
        icon.setFixedSize(56, 56)
        icon.setStyleSheet("background:#ddd; border-radius:8px;")
        icon.setAlignment(Qt.AlignCenter)
        px = QPixmap(os.path.join(dir, "resorces", "dino2.png"))
        if not px.isNull():
            icon.setPixmap(px.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon.setText("🦕")
            icon.setFont(QFont("Segoe UI", 20))
        row.addWidget(icon, alignment=Qt.AlignVCenter)

        # info block
        info = QVBoxLayout()
        info.setSpacing(2)

        name_lbl = QLabel(item["name"])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color:#111; background:transparent;")
        info.addWidget(name_lbl)

        type_lbl = QLabel(f"Type: {item['type']}")
        type_lbl.setFont(QFont("Segoe UI", 9))
        type_lbl.setStyleSheet("color:#555; background:transparent;")
        info.addWidget(type_lbl)

        # variant colour swatch + label
        var_row = QHBoxLayout()
        var_row.setSpacing(5)
        var_lbl = QLabel("Variant:")
        var_lbl.setFont(QFont("Segoe UI", 9))
        var_lbl.setStyleSheet("color:#555; background:transparent;")
        var_row.addWidget(var_lbl)
        swatch = QLabel()
        swatch.setFixedSize(14, 14)
        swatch.setStyleSheet(f"background:{item['variant']}; border-radius:3px;")
        var_row.addWidget(swatch)
        var_row.addStretch()
        info.addLayout(var_row)

        qty_lbl = QLabel(f"Quantity: {item['qty']}")
        qty_lbl.setFont(QFont("Segoe UI", 9))
        qty_lbl.setStyleSheet("color:#555; background:transparent;")
        info.addWidget(qty_lbl)

        row.addLayout(info, stretch=1)

        # price
        price_lbl = QLabel(f"${item['price'] * item['qty']:,}")
        price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        price_lbl.setStyleSheet("color:#111; background:transparent;")
        price_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(price_lbl, alignment=Qt.AlignVCenter)


# ────────────────────────────────────────────────────────────────────────────
#  CheckoutPage
# ────────────────────────────────────────────────────────────────────────────
class CheckoutPage(QWidget):
    # signals for navigation (parent window connects these)
    go_back_to_cart = None   # set by MainWindow after construction

    def __init__(self, cart_items: list[dict], wallet: int, parent=None):
        super().__init__(parent)
        self.cart_items = [i for i in cart_items if i.get("checked")]
        self.wallet = wallet
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#f0f0f0;")
        root = QHBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(24)

        # ── LEFT: checkout steps (scrollable) ───────────────────────────
        left_outer = QFrame()
        left_outer.setStyleSheet("QFrame{background:#fff; border-radius:14px;}")

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setStyleSheet("background:transparent;")

        left = QWidget()
        left.setStyleSheet("background:transparent;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(28, 24, 28, 24)
        left_layout.setSpacing(20)

        title = QLabel("Checkout")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color:#111;")
        left_layout.addWidget(title)

        self._add_divider(left_layout)

        # 1. Buyer info
        left_layout.addWidget(self._section_label("1. Buyer Information"))
        buyer_frame = QFrame()
        buyer_frame.setStyleSheet("QFrame{background:#f7f7f7; border-radius:8px;}")
        buyer_layout = QVBoxLayout(buyer_frame)
        buyer_layout.setContentsMargins(14, 12, 14, 12)
        buyer_layout.setSpacing(10)

        buyer_field_style = """
            QLineEdit {
                border: 1px solid #ccc; border-radius: 6px;
                padding: 7px 10px; font-size: 10pt; color: #111; background: #fff;
            }
            QLineEdit:focus { border: 1px solid #0b7a12; }
        """

        # read-only name + wallet row
        info_row = QHBoxLayout()
        for label, value in [("Name", "[username]"), ("Wallet", f"${self.wallet:,}")]:
            col = QVBoxLayout()
            col.setSpacing(2)
            k = QLabel(label)
            k.setFont(QFont("Segoe UI", 9))
            k.setStyleSheet("color:#666; background:transparent;")
            v = QLabel(value)
            v.setFont(QFont("Segoe UI", 10, QFont.Bold))
            v.setStyleSheet("color:#111; background:transparent;")
            col.addWidget(k)
            col.addWidget(v)
            info_row.addLayout(col)
            info_row.addStretch()
        buyer_layout.addLayout(info_row)

        # email + phone input row
        ep_row = QHBoxLayout()
        ep_row.setSpacing(12)

        self.field_email = QLineEdit()
        self.field_email.setPlaceholderText("Email *")
        self.field_email.setFixedHeight(40)
        self.field_email.setStyleSheet(buyer_field_style)

        self.field_phone = QLineEdit()
        self.field_phone.setPlaceholderText("Phone Number *")
        self.field_phone.setFixedHeight(40)
        self.field_phone.setStyleSheet(buyer_field_style)
        from PySide6.QtGui import QRegularExpressionValidator
        from PySide6.QtCore import QRegularExpression
        self.field_phone.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"[\d\+\-\s]{0,20}"), self)
        )

        ep_row.addWidget(self.field_email)
        ep_row.addWidget(self.field_phone)
        buyer_layout.addLayout(ep_row)

        left_layout.addWidget(buyer_frame)

        self._add_divider(left_layout)

        # 2. Shipping Address
        left_layout.addWidget(self._section_label("2. Shipping Address"))

        field_style = """
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 10pt;
                color: #111;
                background: #fff;
            }
            QLineEdit:focus { border: 1px solid #0b7a12; }
            QLineEdit[invalid="true"] { border: 1px solid #cc0000; }
        """

        def make_field(placeholder: str, required: bool = True) -> QLineEdit:
            f = QLineEdit()
            ph = placeholder + (" *" if required else "")
            f.setPlaceholderText(ph)
            f.setFixedHeight(40)
            f.setStyleSheet(field_style)
            return f

        # Name / Postal Code row
        name_row = QHBoxLayout()
        name_row.setSpacing(12)
        self.field_first = make_field("Name")
        self.field_postal = make_field("Postal Code")
        self.field_postal.setMaxLength(10)
        from PySide6.QtGui import QIntValidator
        self.field_postal.setValidator(QIntValidator(0, 9999999, self))
        name_row.addWidget(self.field_first)
        name_row.addWidget(self.field_postal)
        left_layout.addLayout(name_row)

        # Street address
        self.field_street = make_field("Street Address")
        left_layout.addWidget(self.field_street)

        # Apt / Suite (optional)
        self.field_apt = make_field("Apt / Suite / Unit", required=False)
        self.field_apt.setPlaceholderText("Apt / Suite / Unit (Optional)")
        left_layout.addWidget(self.field_apt)

        # City / Province row
        city_prov_row = QHBoxLayout()
        city_prov_row.setSpacing(12)
        self.field_city     = make_field("City")
        self.field_province = make_field("Province")
        city_prov_row.addWidget(self.field_city)
        city_prov_row.addWidget(self.field_province)
        left_layout.addLayout(city_prov_row)

        self._add_divider(left_layout)

        # 3. Total + wallet check info
        total = sum(i["price"] * i["qty"] for i in self.cart_items)
        self.total = total

        total_row = QHBoxLayout()
        total_lbl = QLabel("Total:")
        total_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        total_lbl.setStyleSheet("color:#111;")
        total_val = QLabel(f"${total:,}")
        total_val.setFont(QFont("Segoe UI", 13, QFont.Bold))
        total_val.setStyleSheet("color:#0b7a12;")
        total_val.setAlignment(Qt.AlignRight)
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_row.addWidget(total_val)
        left_layout.addLayout(total_row)

        wallet_row = QHBoxLayout()
        wallet_lbl = QLabel("Wallet balance:")
        wallet_lbl.setFont(QFont("Segoe UI", 10))
        wallet_lbl.setStyleSheet("color:#666;")
        wallet_val = QLabel(f"${self.wallet:,}")
        wallet_val.setFont(QFont("Segoe UI", 10))
        color = "#0b7a12" if self.wallet >= total else "#cc0000"
        wallet_val.setStyleSheet(f"color:{color};")
        wallet_val.setAlignment(Qt.AlignRight)
        wallet_row.addWidget(wallet_lbl)
        wallet_row.addStretch()
        wallet_row.addWidget(wallet_val)
        left_layout.addLayout(wallet_row)

        left_layout.addStretch()

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        back_btn = QPushButton("← Back to Cart")
        back_btn.setFixedHeight(44)
        back_btn.setFont(QFont("Segoe UI", 11))
        back_btn.setStyleSheet("""
            QPushButton{background:#e0e0e0;border:none;border-radius:10px;color:#333;}
            QPushButton:hover{background:#ccc;}
        """)
        back_btn.clicked.connect(self._on_back)
        btn_row.addWidget(back_btn)

        confirm_btn = QPushButton("Confirm & Pay")
        confirm_btn.setFixedHeight(44)
        confirm_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        confirm_btn.setStyleSheet("""
            QPushButton{background:#0b7a12;border:none;border-radius:10px;color:white;}
            QPushButton:hover{background:#095e0e;}
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn, stretch=1)

        left_layout.addLayout(btn_row)

        left_scroll.setWidget(left)
        left_outer_layout = QVBoxLayout(left_outer)
        left_outer_layout.setContentsMargins(0, 0, 0, 0)
        left_outer_layout.addWidget(left_scroll)

        root.addWidget(left_outer, stretch=3)

        # ── RIGHT: order summary panel ───────────────────────────────────
        right = QFrame()
        right.setStyleSheet("QFrame{background:#fff; border-radius:14px;}")
        right.setFixedWidth(340)
        right_outer = QVBoxLayout(right)
        right_outer.setContentsMargins(0, 0, 0, 0)
        right_outer.setSpacing(0)

        # title (fixed, outside scroll)
        title_bar = QWidget()
        title_bar.setStyleSheet("background:transparent;")
        title_bar_layout = QVBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 20, 20, 8)
        summary_title = QLabel("Order Summary")
        summary_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        summary_title.setStyleSheet("color:#111;")
        title_bar_layout.addWidget(summary_title)
        right_outer.addWidget(title_bar)

        # scrollable area for item cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background:transparent;")

        items_widget = QWidget()
        items_widget.setStyleSheet("background:transparent;")
        items_layout = QVBoxLayout(items_widget)
        items_layout.setContentsMargins(20, 4, 20, 4)
        items_layout.setSpacing(8)

        for item in self.cart_items:
            items_layout.addWidget(OrderSummaryItem(item))
        items_layout.addStretch()

        scroll.setWidget(items_widget)
        right_outer.addWidget(scroll, stretch=1)

        # fixed footer: subtotal / total
        footer = QWidget()
        footer.setStyleSheet("background:transparent;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 8, 20, 20)
        footer_layout.setSpacing(6)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#e0e0e0;")
        footer_layout.addWidget(line)

        subtotal = total
        for label, value in [("Subtotal", f"${subtotal:,}"), ("Shipping", "Free")]:
            r = QHBoxLayout()
            l = QLabel(label)
            l.setFont(QFont("Segoe UI", 10))
            l.setStyleSheet("color:#555; background:transparent;")
            v = QLabel(value)
            v.setFont(QFont("Segoe UI", 10))
            v.setStyleSheet("color:#111; background:transparent;")
            v.setAlignment(Qt.AlignRight)
            r.addWidget(l); r.addStretch(); r.addWidget(v)
            footer_layout.addLayout(r)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color:#e0e0e0;")
        footer_layout.addWidget(line2)

        total_r = QHBoxLayout()
        tl = QLabel("Total")
        tl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        tl.setStyleSheet("color:#111; background:transparent;")
        tv = QLabel(f"${total:,}")
        tv.setFont(QFont("Segoe UI", 12, QFont.Bold))
        tv.setStyleSheet("color:#0b7a12; background:transparent;")
        tv.setAlignment(Qt.AlignRight)
        total_r.addWidget(tl); total_r.addStretch(); total_r.addWidget(tv)
        footer_layout.addLayout(total_r)

        right_outer.addWidget(footer)
        root.addWidget(right, stretch=0)

    # ── helpers ─────────────────────────────────────────────────────────────
    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("color:#333;")
        return lbl

    def _add_divider(self, layout: QVBoxLayout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#e0e0e0;")
        line.setFixedHeight(1)
        layout.addWidget(line)

    # ── flowchart logic ──────────────────────────────────────────────────────
    def _on_back(self):
        # "Go back to cart" branch
        QMessageBox.information(self, "Navigation", "Going back to Cart...")

    def _validate_shipping(self) -> bool:
        """Highlight empty required fields and return True if all valid."""
        required = [
            (self.field_email,   "Email"),
            (self.field_phone,   "Phone Number"),
            (self.field_first,   "Name"),
            (self.field_street,  "Street Address"),
            (self.field_city,    "City"),
            (self.field_province,"Province"),
            (self.field_postal,  "Postal Code"),
        ]
        errors = []
        for field, label in required:
            empty = field.text().strip() == ""
            field.setProperty("invalid", "true" if empty else "false")
            field.style().unpolish(field)
            field.style().polish(field)
            if empty:
                errors.append(label)

        # basic email format check
        if not errors or "Email" not in errors:
            import re
            if self.field_email.text().strip() and not re.match(r"[^@]+@[^@]+\.[^@]+", self.field_email.text().strip()):
                self.field_email.setProperty("invalid", "true")
                self.field_email.style().unpolish(self.field_email)
                self.field_email.style().polish(self.field_email)
                errors.append("Email (invalid format)")

        if errors:
            QMessageBox.warning(
                self, "Missing Information",
                "Please fix the following fields:\n• " + "\n• ".join(errors)
            )
            return False
        return True

    def _on_confirm(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Order", "No items selected.")
            return

        # Validate shipping address first
        if not self._validate_shipping():
            return

        # Check wallet
        if self.wallet < self.total:
            reply = QMessageBox.question(
                self, "Insufficient Funds",
                f"Your wallet (${self.wallet:,}) is not enough for this order (${self.total:,}).\n\n"
                "Do you want to add funds to your wallet?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Navigation", "Going to Wallet top-up page...")
            else:
                QMessageBox.information(self, "Navigation", "Going back to Store...")
            return

        # Wallet sufficient → update stock + success
        self._update_stock()
        QMessageBox.information(
            self, "Order Successful",
            f"Your order has been placed!\nTotal charged: ${self.total:,}"
        )

    def _update_stock(self):
        # Placeholder: in real app, call DB / backend here
        for item in self.cart_items:
            print(f"[DB] Reduce stock: {item['name']} by {item['qty']}")


# ────────────────────────────────────────────────────────────────────────────
#  MainWindow
# ────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart – Checkout")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()

        checked_items = [i for i in CART_ITEMS if i.get("checked")]
        self.setCentralWidget(CheckoutPage(checked_items, WALLET_BALANCE))

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
        container.setStyleSheet("QWidget{background:#0b7a12;}")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        icon_style = (
            "QPushButton{color:white;background:transparent;border:none;padding:5px;}"
            "QPushButton:hover{background-color:rgba(255,255,255,0.2);border-radius:22px;}"
        )

        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40, 40))
        self.logo.setFixedSize(44, 44)
        self.logo.setStyleSheet(icon_style)

        font_path = os.path.join(dir, "resorces", "DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        name_font = QFont(families[0], 18) if families else QFont("Segoe UI", 18, QFont.Bold)

        self.name_btn = QPushButton("JurassiCart")
        self.name_btn.setFont(name_font)
        self.name_btn.setStyleSheet(
            "QPushButton{color:white;background:transparent;border:none;}"
            "QPushButton:hover{color:#ccffcc;}"
        )

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
        search_icon.setStyleSheet(
            "QPushButton{background:transparent;border:none;}"
            "QPushButton:hover{background:#ddd;border-radius:18px;}"
        )
        search_icon.clicked.connect(lambda: print("Search"))
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        self.filter_btn = QPushButton()
        self.filter_btn.setIcon(QIcon(os.path.join(dir, "resorces", "filter.png")))
        self.filter_btn.setIconSize(QSize(28, 28))
        self.filter_btn.setFixedSize(44, 44)
        self.filter_btn.setStyleSheet(icon_style)

        self.cart_btn = QPushButton()
        self.cart_btn.setIcon(QIcon(os.path.join(dir, "resorces", "cart.png")))
        self.cart_btn.setIconSize(QSize(36, 36))
        self.cart_btn.setFixedSize(44, 44)
        self.cart_btn.setStyleSheet(icon_style)

        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(os.path.join(dir, "resorces", "user.png")))
        self.profile_btn.setIconSize(QSize(36, 36))
        self.profile_btn.setFixedSize(44, 44)
        self.profile_btn.setStyleSheet(icon_style)

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


# ────────────────────────────────────────────────────────────────────────────
#  Entry point
# ────────────────────────────────────────────────────────────────────────────
def main():
    myappid = "dme.jurassicart.checkout"
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
