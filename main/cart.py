import sys, os
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame,
    QSizePolicy, QToolBar, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon

import database as db

_dir       = os.path.dirname(os.path.abspath(__file__))
dino_logo  = os.path.join(_dir, "resorces", "dino2.png")
juras_logo = os.path.join(_dir, "resorces", "JurassiLogo.png")


# ─────────────────────────────────────────────
#  CartItemRow
# ─────────────────────────────────────────────
class CartItemRow(QFrame):
    changed = Signal()
    deleted = Signal(str)   # emits cart_id

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.item = item   # dict with cart_id, dino_name, gene, color, price, qty, checked
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("CartItemRow{background:#e8e8e8;border-radius:10px;}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)

        self.chk = QCheckBox()
        self.chk.setChecked(self.item.get("checked", True))
        self.chk.setFixedSize(24, 24)
        self.chk.setStyleSheet("QCheckBox::indicator{width:20px;height:20px;}")
        self.chk.stateChanged.connect(self._on_check)
        row.addWidget(self.chk, alignment=Qt.AlignVCenter)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(60, 60)
        icon_lbl.setStyleSheet("background:#bbb;border-radius:8px;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        px = QPixmap(dino_logo)
        if not px.isNull():
            icon_lbl.setPixmap(px.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setText("🦕")
            icon_lbl.setFont(QFont("Segoe UI", 22))
        row.addWidget(icon_lbl, alignment=Qt.AlignVCenter)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_name = QLabel(self.item["dino_name"])
        lbl_name.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_name.setStyleSheet("color:#111;background:transparent;")
        info.addWidget(lbl_name)

        lbl_type = QLabel(self.item.get("gene", ""))
        lbl_type.setFont(QFont("Segoe UI", 9))
        lbl_type.setStyleSheet("color:#555;background:transparent;")
        info.addWidget(lbl_type)

        var_row = QHBoxLayout()
        var_row.setSpacing(6)
        var_lbl = QLabel("Variant")
        var_lbl.setFont(QFont("Segoe UI", 9))
        var_lbl.setStyleSheet("color:#555;background:transparent;")
        var_row.addWidget(var_lbl)
        color_box = QLabel()
        color_box.setFixedSize(18, 18)
        color_box.setStyleSheet(f"background:{self.item.get('color','#888')};border-radius:3px;")
        var_row.addWidget(color_box)
        var_row.addStretch()
        info.addLayout(var_row)
        row.addLayout(info, stretch=1)

        price_lbl = QLabel(f"${int(self.item['price']):,}")
        price_lbl.setFont(QFont("Segoe UI", 11))
        price_lbl.setStyleSheet("color:#111;")
        price_lbl.setFixedWidth(130)
        price_lbl.setAlignment(Qt.AlignCenter)
        row.addWidget(price_lbl)

        qty_frame = QFrame()
        qty_frame.setStyleSheet("QFrame{background:#d0d0d0;border-radius:14px;}")
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

        btn_del = QPushButton("Delete")
        btn_del.setFixedSize(80, 32)
        btn_del.setStyleSheet("""
            QPushButton{background:#d0d0d0;border:none;border-radius:14px;font-size:10pt;color:#111;}
            QPushButton:hover{background:#bbb;}
        """)
        btn_del.clicked.connect(self._on_delete)
        row.addWidget(btn_del, alignment=Qt.AlignVCenter)

    def _qty_up(self):
        # cap at available stock in DB
        dino = db.get_dinosaur(self.item.get("dino_id", ""))
        max_stock = int(dino["stock"]) if dino else 999
        current_qty = int(self.item["qty"])
        if current_qty >= max_stock:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Stock limit",
                                f"Only {max_stock} unit(s) available in stock.")
            return
        self.item["qty"] = current_qty + 1
        self.qty_lbl.setText(str(self.item["qty"]))
        db.update_cart_qty(self.item["cart_id"], self.item["qty"])
        self.changed.emit()

    def _qty_dn(self):
        if int(self.item["qty"]) > 1:
            self.item["qty"] = int(self.item["qty"]) - 1
            self.qty_lbl.setText(str(self.item["qty"]))
            db.update_cart_qty(self.item["cart_id"], self.item["qty"])
            self.changed.emit()

    def _on_check(self):
        self.item["checked"] = self.chk.isChecked()
        self.changed.emit()

    def _on_delete(self):
        db.remove_from_cart(self.item["cart_id"])
        self.deleted.emit(self.item["cart_id"])
        self.setParent(None)
        self.deleteLater()
        self.changed.emit()


# ─────────────────────────────────────────────
#  CartPage
# ─────────────────────────────────────────────
class CartPage(QWidget):
    go_checkout = Signal(list, int)   # (checked_items, wallet)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user: dict | None = None
        self.rows: list[CartItemRow] = []
        self._build_ui()

    def load_user(self, user: dict):
        """Called by MainWindow after login."""
        self._user = user
        self._reload_from_db()

    def add_item(self, dino: dict):
        """Called from store page to add a dino to cart."""
        if not self._user:
            return
        cart_row = db.add_to_cart(self._user["user_id"], dino)
        # check if row widget already exists → update qty label
        for row in self.rows:
            if row.item["cart_id"] == cart_row["cart_id"]:
                row.item["qty"] = int(cart_row["qty"])
                row.qty_lbl.setText(str(row.item["qty"]))
                self._refresh_total()
                return
        # new row
        cart_row["qty"] = int(cart_row["qty"])
        cart_row["checked"] = True
        self._add_row(cart_row)
        self._refresh_total()

    def _reload_from_db(self):
        # clear existing rows
        for row in self.rows:
            row.setParent(None)
            row.deleteLater()
        self.rows.clear()

        if not self._user:
            self._refresh_total()
            return

        items = db.get_cart(self._user["user_id"])
        for item in items:
            item["qty"] = int(item["qty"])
            item["checked"] = True
            self._add_row(item)
        self._refresh_total()

    def _build_ui(self):
        self.setStyleSheet("background:#f0f0f0;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 0)
        outer.setSpacing(0)

        card = QFrame()
        card.setStyleSheet("QFrame{background:#fff;border-radius:14px;}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        title = QLabel("Cart")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color:#111;")
        card_layout.addWidget(title)

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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(8)
        self.rows_layout.addStretch()

        scroll.setWidget(self.rows_container)
        card_layout.addWidget(scroll, stretch=1)
        outer.addWidget(card, stretch=1)

        # bottom bar
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

        self.lbl_total = QLabel("Total(0 items): $0")
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
        btn_order.clicked.connect(self._on_order)
        bottom_layout.addWidget(btn_order)
        outer.addWidget(bottom)

    def _add_row(self, item: dict):
        row = CartItemRow(item)
        row.changed.connect(self._refresh_total)
        row.deleted.connect(self._on_row_deleted)
        idx = self.rows_layout.count() - 1
        self.rows_layout.insertWidget(idx, row)
        self.rows.append(row)

    def _on_row_deleted(self, cart_id: str):
        self.rows = [r for r in self.rows if r.item.get("cart_id") != cart_id]
        self._refresh_total()

    def _refresh_total(self):
        checked = [r.item for r in self.rows if not r.isHidden() and r.item.get("checked")]
        total = sum(int(i["price"]) * int(i["qty"]) for i in checked)
        count = sum(int(i["qty"]) for i in checked)
        self.lbl_total.setText(f"Total({count} item{'s' if count != 1 else ''}): ${total:,}")

    def _select_all(self, state):
        for row in self.rows:
            row.chk.setChecked(bool(state))

    def _on_order(self):
        checked = [r.item for r in self.rows if r.item.get("checked")]
        if not checked:
            QMessageBox.warning(self, "No items", "Please select at least one item.")
            return
        wallet = db.get_wallet(self._user["user_id"]) if self._user else 0
        self.go_checkout.emit(checked, wallet)


# ─────────────────────────────────────────────
#  OrderSummaryItem (used by CheckoutPage)
# ─────────────────────────────────────────────
class OrderSummaryItem(QFrame):
    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame{background:#f7f7f7;border-radius:10px;}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 10, 10, 10)
        row.setSpacing(12)

        icon = QLabel()
        icon.setFixedSize(56, 56)
        icon.setStyleSheet("background:#ddd;border-radius:8px;")
        icon.setAlignment(Qt.AlignCenter)
        px = QPixmap(dino_logo)
        if not px.isNull():
            icon.setPixmap(px.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon.setText("🦕")
            icon.setFont(QFont("Segoe UI", 20))
        row.addWidget(icon, alignment=Qt.AlignVCenter)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(item["dino_name"])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color:#111;background:transparent;")
        info.addWidget(name_lbl)

        type_lbl = QLabel(f"Type: {item.get('gene','')}")
        type_lbl.setFont(QFont("Segoe UI", 9))
        type_lbl.setStyleSheet("color:#555;background:transparent;")
        info.addWidget(type_lbl)

        var_row = QHBoxLayout()
        var_row.setSpacing(5)
        var_lbl = QLabel("Variant:")
        var_lbl.setFont(QFont("Segoe UI", 9))
        var_lbl.setStyleSheet("color:#555;background:transparent;")
        var_row.addWidget(var_lbl)
        swatch = QLabel()
        swatch.setFixedSize(14, 14)
        swatch.setStyleSheet(f"background:{item.get('color','#888')};border-radius:3px;")
        var_row.addWidget(swatch)
        var_row.addStretch()
        info.addLayout(var_row)

        qty_lbl = QLabel(f"Quantity: {item['qty']}")
        qty_lbl.setFont(QFont("Segoe UI", 9))
        qty_lbl.setStyleSheet("color:#555;background:transparent;")
        info.addWidget(qty_lbl)
        row.addLayout(info, stretch=1)

        price_lbl = QLabel(f"${int(item['price']) * int(item['qty']):,}")
        price_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        price_lbl.setStyleSheet("color:#111;background:transparent;")
        price_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(price_lbl, alignment=Qt.AlignVCenter)


# ─────────────────────────────────────────────
#  CheckoutPage
# ─────────────────────────────────────────────
class CheckoutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart_items: list[dict] = []
        self.wallet: int = 0
        self._user: dict | None = None
        self.total: int = 0

    def load(self, cart_items: list[dict], wallet: int, user: dict | None = None):
        """Called by MainWindow before showing this page."""
        self.cart_items = cart_items
        self.wallet = wallet
        self._user = user
        self.total = sum(int(i["price"]) * int(i["qty"]) for i in cart_items)

        # remove old inner widget and replace with fresh one
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                child = old_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            # detach layout by reparenting to a temp widget
            QWidget().setLayout(old_layout)

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#f0f0f0;")
        root = QHBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(24)

        # LEFT scrollable
        left_outer = QFrame()
        left_outer.setStyleSheet("QFrame{background:#fff;border-radius:14px;}")
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        buyer_frame.setStyleSheet("QFrame{background:#f7f7f7;border-radius:8px;}")
        buyer_layout = QVBoxLayout(buyer_frame)
        buyer_layout.setContentsMargins(14, 12, 14, 12)
        buyer_layout.setSpacing(10)

        field_style = ("QLineEdit{border:1px solid #ccc;border-radius:6px;"
                       "padding:7px 10px;font-size:10pt;color:#111;background:#fff;}"
                       "QLineEdit:focus{border:1px solid #0b7a12;}")

        info_row = QHBoxLayout()
        uname = self._user["username"] if self._user else "[username]"
        for label, value in [("Name", uname), ("Wallet", f"${self.wallet:,}")]:
            col = QVBoxLayout(); col.setSpacing(2)
            k = QLabel(label); k.setFont(QFont("Segoe UI", 9))
            k.setStyleSheet("color:#666;background:transparent;")
            v = QLabel(value); v.setFont(QFont("Segoe UI", 10, QFont.Bold))
            v.setStyleSheet("color:#111;background:transparent;")
            col.addWidget(k); col.addWidget(v)
            info_row.addLayout(col); info_row.addStretch()
        buyer_layout.addLayout(info_row)

        ep_row = QHBoxLayout(); ep_row.setSpacing(12)
        self.field_email = QLineEdit()
        self.field_email.setPlaceholderText("Email *")
        self.field_email.setFixedHeight(40)
        self.field_email.setStyleSheet(field_style)
        if self._user:
            self.field_email.setText(self._user.get("email", ""))

        self.field_phone = QLineEdit()
        self.field_phone.setPlaceholderText("Phone Number *")
        self.field_phone.setFixedHeight(40)
        self.field_phone.setStyleSheet(field_style)
        if self._user:
            self.field_phone.setText(self._user.get("phone", ""))

        ep_row.addWidget(self.field_email); ep_row.addWidget(self.field_phone)
        buyer_layout.addLayout(ep_row)
        left_layout.addWidget(buyer_frame)
        self._add_divider(left_layout)

        # 2. Shipping
        left_layout.addWidget(self._section_label("2. Shipping Address"))
        sh_style = ("QLineEdit{border:1px solid #ccc;border-radius:6px;"
                    "padding:8px 10px;font-size:10pt;color:#111;background:#fff;}"
                    "QLineEdit:focus{border:1px solid #0b7a12;}"
                    "QLineEdit[invalid='true']{border:1px solid #cc0000;}")

        def mf(ph, req=True):
            f = QLineEdit()
            f.setPlaceholderText(ph + (" *" if req else ""))
            f.setFixedHeight(40); f.setStyleSheet(sh_style)
            return f

        nr = QHBoxLayout(); nr.setSpacing(12)
        self.field_first = mf("Name")
        self.field_postal = mf("Postal Code")
        self.field_postal.setMaxLength(10)
        from PySide6.QtGui import QIntValidator
        self.field_postal.setValidator(QIntValidator(0, 9999999, self))
        nr.addWidget(self.field_first); nr.addWidget(self.field_postal)
        left_layout.addLayout(nr)

        self.field_street = mf("Street Address")
        left_layout.addWidget(self.field_street)
        self.field_apt = QLineEdit()
        self.field_apt.setPlaceholderText("Apt / Suite / Unit (Optional)")
        self.field_apt.setFixedHeight(40); self.field_apt.setStyleSheet(sh_style)
        left_layout.addWidget(self.field_apt)

        cr = QHBoxLayout(); cr.setSpacing(12)
        self.field_city = mf("City")
        self.field_province = mf("Province")
        cr.addWidget(self.field_city); cr.addWidget(self.field_province)
        left_layout.addLayout(cr)
        self._add_divider(left_layout)

        # 3. Total
        tr = QHBoxLayout()
        tl = QLabel("Total:"); tl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        tl.setStyleSheet("color:#111;")
        tv = QLabel(f"${self.total:,}"); tv.setFont(QFont("Segoe UI", 13, QFont.Bold))
        tv.setStyleSheet("color:#0b7a12;"); tv.setAlignment(Qt.AlignRight)
        tr.addWidget(tl); tr.addStretch(); tr.addWidget(tv)
        left_layout.addLayout(tr)

        wr = QHBoxLayout()
        wl = QLabel("Wallet balance:"); wl.setFont(QFont("Segoe UI", 10))
        wl.setStyleSheet("color:#666;")
        wv = QLabel(f"${self.wallet:,}"); wv.setFont(QFont("Segoe UI", 10))
        wv.setStyleSheet(f"color:{'#0b7a12' if self.wallet >= self.total else '#cc0000'};")
        wv.setAlignment(Qt.AlignRight)
        wr.addWidget(wl); wr.addStretch(); wr.addWidget(wv)
        left_layout.addLayout(wr)
        left_layout.addStretch()

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        back_btn = QPushButton("← Back to Cart")
        back_btn.setFixedHeight(44)
        back_btn.setFont(QFont("Segoe UI", 11))
        back_btn.setStyleSheet("QPushButton{background:#e0e0e0;border:none;border-radius:10px;color:#333;}"
                               "QPushButton:hover{background:#ccc;}")
        back_btn.clicked.connect(self._on_back)
        btn_row.addWidget(back_btn)

        confirm_btn = QPushButton("Confirm & Pay")
        confirm_btn.setFixedHeight(44)
        confirm_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        confirm_btn.setStyleSheet("QPushButton{background:#0b7a12;border:none;border-radius:10px;color:white;}"
                                  "QPushButton:hover{background:#095e0e;}")
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn, stretch=1)
        left_layout.addLayout(btn_row)

        left_scroll.setWidget(left)
        lo = QVBoxLayout(left_outer); lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(left_scroll)
        root.addWidget(left_outer, stretch=3)

        # RIGHT summary
        right = QFrame()
        right.setStyleSheet("QFrame{background:#fff;border-radius:14px;}")
        right.setFixedWidth(340)
        ro = QVBoxLayout(right); ro.setContentsMargins(0, 0, 0, 0); ro.setSpacing(0)

        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QVBoxLayout(tb); tbl.setContentsMargins(20, 20, 20, 8)
        st = QLabel("Order Summary"); st.setFont(QFont("Segoe UI", 14, QFont.Bold))
        st.setStyleSheet("color:#111;"); tbl.addWidget(st)
        ro.addWidget(tb)

        sc2 = QScrollArea(); sc2.setWidgetResizable(True)
        sc2.setFrameShape(QFrame.NoFrame)
        sc2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sc2.setStyleSheet("background:transparent;")
        iw = QWidget(); iw.setStyleSheet("background:transparent;")
        il = QVBoxLayout(iw)
        il.setContentsMargins(20, 4, 20, 4)
        il.setSpacing(8)
        for item in self.cart_items:
            il.addWidget(OrderSummaryItem(item))
        il.addStretch()
        sc2.setWidget(iw); ro.addWidget(sc2, stretch=1)

        ft = QWidget(); ft.setStyleSheet("background:transparent;")
        fl = QVBoxLayout(ft); fl.setContentsMargins(20, 8, 20, 20); fl.setSpacing(6)
        ln = QFrame(); ln.setFrameShape(QFrame.HLine); ln.setStyleSheet("color:#e0e0e0;")
        fl.addWidget(ln)
        for lbl, val in [("Subtotal", f"${self.total:,}"), ("Shipping", "Free")]:
            rr = QHBoxLayout()
            ll = QLabel(lbl); ll.setFont(QFont("Segoe UI", 10))
            ll.setStyleSheet("color:#555;background:transparent;")
            vv = QLabel(val); vv.setFont(QFont("Segoe UI", 10))
            vv.setStyleSheet("color:#111;background:transparent;"); vv.setAlignment(Qt.AlignRight)
            rr.addWidget(ll); rr.addStretch(); rr.addWidget(vv); fl.addLayout(rr)
        ln2 = QFrame(); ln2.setFrameShape(QFrame.HLine); ln2.setStyleSheet("color:#e0e0e0;")
        fl.addWidget(ln2)
        tot_r = QHBoxLayout()
        tll = QLabel("Total"); tll.setFont(QFont("Segoe UI", 12, QFont.Bold))
        tll.setStyleSheet("color:#111;background:transparent;")
        tvv = QLabel(f"${self.total:,}"); tvv.setFont(QFont("Segoe UI", 12, QFont.Bold))
        tvv.setStyleSheet("color:#0b7a12;background:transparent;"); tvv.setAlignment(Qt.AlignRight)
        tot_r.addWidget(tll); tot_r.addStretch(); tot_r.addWidget(tvv); fl.addLayout(tot_r)
        ro.addWidget(ft)
        root.addWidget(right, stretch=0)

    def _section_label(self, text):
        lbl = QLabel(text); lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("color:#333;"); return lbl

    def _add_divider(self, layout):
        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#e0e0e0;"); line.setFixedHeight(1)
        layout.addWidget(line)

    def _on_back(self):
        # MainWindow will handle navigation
        parent = self.parent()
        while parent and not hasattr(parent, 'go'):
            parent = parent.parent()
        if parent:
            parent.go(parent.cart)

    def _validate(self) -> bool:
        required = [
            (self.field_email,    "Email"),
            (self.field_phone,    "Phone Number"),
            (self.field_first,    "Name"),
            (self.field_street,   "Street Address"),
            (self.field_city,     "City"),
            (self.field_province, "Province"),
            (self.field_postal,   "Postal Code"),
        ]
        errors = []
        for field, label in required:
            empty = field.text().strip() == ""
            field.setProperty("invalid", "true" if empty else "false")
            field.style().unpolish(field); field.style().polish(field)
            if empty:
                errors.append(label)
        import re
        if self.field_email.text().strip() and \
                not re.match(r"[^@]+@[^@]+\.[^@]+", self.field_email.text().strip()):
            self.field_email.setProperty("invalid", "true")
            self.field_email.style().unpolish(self.field_email)
            self.field_email.style().polish(self.field_email)
            errors.append("Email (invalid format)")
        if errors:
            QMessageBox.warning(self, "Missing Information",
                                "Please fix:\n• " + "\n• ".join(errors))
            return False
        return True

    def _on_confirm(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Order", "No items selected."); return
        if not self._validate():
            return
        if self.wallet < self.total:
            reply = QMessageBox.question(
                self, "Insufficient Funds",
                f"Wallet (${self.wallet:,}) < Order (${self.total:,}).\n"
                "Add funds to wallet?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # navigate to account page → wallet tab
                parent = self.parent()
                while parent and not hasattr(parent, 'account'):
                    parent = parent.parent()
                if parent:
                    parent.account.tab_bar._on_click(1)   # switch to Wallet tab
                    parent.go(parent.account)
            else:
                # go back to store
                parent = self.parent()
                while parent and not hasattr(parent, 'store'):
                    parent = parent.parent()
                if parent:
                    parent.go(parent.store)
            return

        if self._user:
            shipping = {
                "name":    self.field_first.text().strip(),
                "address": f"{self.field_street.text()}, {self.field_city.text()}, "
                           f"{self.field_province.text()} {self.field_postal.text()}",
                "email":   self.field_email.text().strip(),
                "phone":   self.field_phone.text().strip(),
            }
            order = db.create_order(self._user["user_id"], self.cart_items, shipping)
            if order:
                db.clear_cart(self._user["user_id"])
                QMessageBox.information(
                    self, "Order Successful",
                    f"Order placed!\nEstimated delivery: {order['delivery_days']} days\n"
                    f"Total charged: ${self.total:,}")
                # reload cart and refresh home stock display
                parent = self.parent()
                while parent and not hasattr(parent, 'cart'):
                    parent = parent.parent()
                if parent:
                    parent.cart._reload_from_db()
                    parent.home.refresh()   # update stock counts on home
                    parent.go(parent.home)
            else:
                QMessageBox.warning(self, "Error", "Order failed. Please try again.")
