import sys, os
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame,
    QSizePolicy, QToolBar, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon

dir = os.path.dirname(os.path.abspath(__file__))
dino_logo  = os.path.join(dir, "resorces", "dino2.png")
juras_logo = os.path.join(dir, "resorces", "JurassiLogo.png")

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
