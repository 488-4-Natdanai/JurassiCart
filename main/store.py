import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QFileDialog, QSizePolicy,
    QScrollArea, QGridLayout, QStackedWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QColorDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QPainterPath

dir_path = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────── constants ──────────────────────────────
GREEN       = "#0b7a12"
GREEN_HOVER = "#0a6610"

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
    QPushButton:hover {{ background-color: {hover}; }}
    QPushButton:pressed {{ background-color: #085c0e; }}
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
    QLineEdit:focus, QComboBox:focus { border: 1.5px solid #0b7a12; }
    QComboBox::drop-down { border: none; width: 24px; }
    QComboBox::down-arrow { width: 12px; height: 12px; }
"""
LABEL_STYLE = "font-size: 13px; color: #333333;"


# ─────────────────────── helpers ────────────────────────────────
def make_tab_btn(text):
    btn = QPushButton(text)
    btn.setCheckable(True)
    btn.setMinimumWidth(130)
    btn.setMinimumHeight(42)
    btn.setFont(QFont("Segoe UI", 11))
    return btn


def apply_tab_styles(buttons, active_index):
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
                QPushButton:hover { background: #d8d8d8; }
            """)
            btn.setChecked(False)


def color_swatch(color: QColor, size=20) -> QLabel:
    """Return a small square label filled with color."""
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    pix = QPixmap(size, size)
    pix.fill(color)
    lbl.setPixmap(pix)
    lbl.setStyleSheet("border: 1px solid #888;")
    return lbl


# ══════════════════════ Store Profile ═══════════════════════════
class StoreProfilePage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(60)

        # ── left: form ──
        form_widget = QWidget()
        form = QGridLayout(form_widget)
        form.setVerticalSpacing(16)
        form.setHorizontalSpacing(16)
        form.setColumnStretch(1, 1)

        lbl = QLabel("Store name")
        lbl.setStyleSheet(LABEL_STYLE)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.store_name_inp = QLineEdit("Jane Doe")
        self.store_name_inp.setStyleSheet(INPUT_STYLE)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BTN_STYLE.format(bg=GREEN, hover=GREEN_HOVER))
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(lambda: print(f"Store name saved: {self.store_name_inp.text()}"))

        form.addWidget(lbl, 0, 0)
        form.addWidget(self.store_name_inp, 0, 1)
        form.addWidget(save_btn, 1, 1, alignment=Qt.AlignLeft)

        root.addWidget(form_widget, stretch=2)

        # ── right: avatar ──
        av_widget = QWidget()
        av_layout = QVBoxLayout(av_widget)
        av_layout.setAlignment(Qt.AlignCenter)
        av_layout.setSpacing(12)

        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(110, 110)
        self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setFont(QFont("Segoe UI Emoji", 40))
        self.avatar_lbl.setText("👤")
        self.avatar_lbl.setStyleSheet("""
            QLabel {
                background-color: #b0b0b0;
                border-radius: 55px;
            }
        """)

        sel_btn = QPushButton("Select Image")
        sel_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #aaaaaa;
                border-radius: 12px; font-size: 12px;
                padding: 5px 16px; color: #333;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)
        sel_btn.clicked.connect(self._pick_image)

        av_layout.addStretch()
        av_layout.addWidget(self.avatar_lbl, alignment=Qt.AlignCenter)
        av_layout.addWidget(sel_btn, alignment=Qt.AlignCenter)
        av_layout.addStretch()

        root.addWidget(av_widget, stretch=1)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            pix = QPixmap(path).scaled(110, 110, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.avatar_lbl.setText("")
            self.avatar_lbl.setPixmap(pix)


# ══════════════════════════ Stock ═══════════════════════════════
class StockPage(QWidget):
    def __init__(self, stock_data: list):
        """stock_data: list of dicts {name, gene, price, gender, variant_color, image_path}"""
        super().__init__()
        self.stock_data = stock_data
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setSpacing(0)
        self.list_layout.setContentsMargins(0, 0, 0, 0)

        self._rebuild_rows()

        self.list_layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

    def _rebuild_rows(self):
        # clear
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # header row
        header = self._make_row_widget(
            ["", "", "Name", "Price", ""], is_header=True
        )
        self.list_layout.addWidget(header)

        for i, item in enumerate(self.stock_data):
            row = self._make_stock_row(i + 1, item)
            self.list_layout.addWidget(row)

    def _make_row_widget(self, cols, is_header=False):
        w = QWidget()
        w.setFixedHeight(30)
        w.setStyleSheet("background: #c8c8c8; border: 1px solid #bbbbbb;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(8, 2, 8, 2)
        lay.setSpacing(0)
        for c in cols:
            lbl = QLabel(str(c))
            lbl.setStyleSheet("background:transparent; border:none; font-size:12px; color:#333;")
            lay.addWidget(lbl, stretch=1)
        return w

    def _make_stock_row(self, number: int, item: dict):
        row = QWidget()
        row.setFixedHeight(70)
        bg = "#e8e8e8" if number % 2 == 0 else "#d8d8d8"
        row.setStyleSheet(f"background: {bg}; border: 1px solid #bbbbbb;")

        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(10)

        # number
        num_lbl = QLabel(str(number))
        num_lbl.setFixedWidth(24)
        num_lbl.setStyleSheet("background:transparent; border:none; font-size:13px;")
        lay.addWidget(num_lbl)

        # image thumbnail
        img_lbl = QLabel()
        img_lbl.setFixedSize(54, 54)
        img_lbl.setStyleSheet("background:#b0b0b0; border-radius:4px; border:none;")
        img_lbl.setAlignment(Qt.AlignCenter)
        if item.get("image_path") and os.path.exists(item["image_path"]):
            pix = QPixmap(item["image_path"]).scaled(54, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText("🦕")
            img_lbl.setFont(QFont("Segoe UI Emoji", 22))
        lay.addWidget(img_lbl)

        # info block
        info = QWidget()
        info.setStyleSheet("background:transparent; border:none;")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(2)

        name_lbl = QLabel(item.get("name", ""))
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("background:transparent; border:none;")

        gene_lbl = QLabel(item.get("gene", ""))
        gene_lbl.setFont(QFont("Segoe UI", 9))
        gene_lbl.setStyleSheet("background:transparent; border:none; color:#555;")

        variant_row = QWidget()
        variant_row.setStyleSheet("background:transparent; border:none;")
        variant_row_lay = QHBoxLayout(variant_row)
        variant_row_lay.setContentsMargins(0, 0, 0, 0)
        variant_row_lay.setSpacing(4)

        var_lbl = QLabel("Variant")
        var_lbl.setFont(QFont("Segoe UI", 9))
        var_lbl.setStyleSheet("background:transparent; border:none; color:#555;")

        color = item.get("variant_color", QColor("#888888"))
        swatch = color_swatch(color, 16)

        variant_row_lay.addWidget(var_lbl)
        variant_row_lay.addWidget(swatch)
        variant_row_lay.addStretch()

        info_lay.addWidget(name_lbl)
        info_lay.addWidget(gene_lbl)
        info_lay.addWidget(variant_row)

        lay.addWidget(info, stretch=3)

        # price
        price_lbl = QLabel(f"${item.get('price', 0):,.0f}")
        price_lbl.setFont(QFont("Segoe UI", 11))
        price_lbl.setStyleSheet("background:transparent; border:none;")
        lay.addWidget(price_lbl, stretch=2)

        # delete button
        del_btn = QPushButton("Delete")
        del_btn.setFixedWidth(80)
        del_btn.setFixedHeight(30)
        del_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #aaa;
                border-radius: 14px; font-size: 12px; color: #333;
            }
            QPushButton:hover { background: #ffdddd; border-color: #e53935; color: #c62828; }
        """)
        del_btn.clicked.connect(lambda _, n=number-1: self._delete_item(n))
        lay.addWidget(del_btn)

        return row

    def _delete_item(self, index: int):
        if 0 <= index < len(self.stock_data):
            del self.stock_data[index]
            self._rebuild_rows()

    def refresh(self):
        self._rebuild_rows()


# ════════════════════════ Add Stock ═════════════════════════════
class AddStockPage(QWidget):
    def __init__(self, stock_data: list, stock_page: StockPage):
        super().__init__()
        self.stock_data = stock_data
        self.stock_page = stock_page
        self.variant_color = QColor("#2e7d32")
        self.image_path = ""
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(60)

        # ── left: form ──
        form_widget = QWidget()
        form = QGridLayout(form_widget)
        form.setVerticalSpacing(16)
        form.setHorizontalSpacing(16)
        form.setColumnStretch(1, 1)

        # Dinosaur name
        self._add_label_input(form, 0, "Dinosaur", "Tyrannosaurus Rex")

        # Gene
        gene_lbl = QLabel("Gene")
        gene_lbl.setStyleSheet(LABEL_STYLE)
        gene_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.gene_cb = QComboBox()
        self.gene_cb.addItems(["Carnivore", "Herbivore", "Omnivore", "Piscivore"])
        self.gene_cb.setStyleSheet(INPUT_STYLE)
        form.addWidget(gene_lbl, 1, 0)
        form.addWidget(self.gene_cb, 1, 1)

        # Price
        self._add_label_input(form, 2, "Price", "$25,000,000", attr="price_inp")

        # Gender
        gender_lbl = QLabel("Gender")
        gender_lbl.setStyleSheet(LABEL_STYLE)
        gender_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.gender_cb = QComboBox()
        self.gender_cb.addItems(["Female", "Male"])
        self.gender_cb.setStyleSheet(INPUT_STYLE)
        form.addWidget(gender_lbl, 3, 0)
        form.addWidget(self.gender_cb, 3, 1)

        # Variant color
        var_lbl = QLabel("Variant")
        var_lbl.setStyleSheet(LABEL_STYLE)
        var_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        variant_row = QWidget()
        variant_row_lay = QHBoxLayout(variant_row)
        variant_row_lay.setContentsMargins(0, 0, 0, 0)
        variant_row_lay.setSpacing(8)

        self.variant_swatch = QLabel()
        self.variant_swatch.setFixedSize(24, 24)
        self.variant_swatch.setStyleSheet(
            f"background:{self.variant_color.name()}; border:1px solid #888;"
        )
        self.variant_swatch.setCursor(Qt.PointingHandCursor)
        self.variant_swatch.mousePressEvent = lambda e: self._pick_color()

        variant_row_lay.addWidget(self.variant_swatch)
        variant_row_lay.addStretch()

        form.addWidget(var_lbl, 4, 0)
        form.addWidget(variant_row, 4, 1)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BTN_STYLE.format(bg=GREEN, hover=GREEN_HOVER))
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self._save)
        form.addWidget(save_btn, 5, 1, alignment=Qt.AlignLeft)

        root.addWidget(form_widget, stretch=2)

        # ── right: image upload ──
        img_widget = QWidget()
        img_lay = QVBoxLayout(img_widget)
        img_lay.setAlignment(Qt.AlignCenter)
        img_lay.setSpacing(12)

        self.img_preview = QLabel()
        self.img_preview.setFixedSize(150, 120)
        self.img_preview.setStyleSheet("""
            QLabel {
                background: #c8c8c8;
                border-radius: 10px;
            }
        """)
        self.img_preview.setAlignment(Qt.AlignCenter)

        sel_btn = QPushButton("Select Image")
        sel_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #aaaaaa;
                border-radius: 12px; font-size: 12px;
                padding: 5px 16px; color: #333;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)
        sel_btn.clicked.connect(self._pick_image)

        img_lay.addStretch()
        img_lay.addWidget(self.img_preview, alignment=Qt.AlignCenter)
        img_lay.addWidget(sel_btn, alignment=Qt.AlignCenter)
        img_lay.addStretch()

        root.addWidget(img_widget, stretch=1)

    def _add_label_input(self, form, row, label_text, placeholder="", attr=None):
        lbl = QLabel(label_text)
        lbl.setStyleSheet(LABEL_STYLE)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        inp = QLineEdit(placeholder)
        inp.setStyleSheet(INPUT_STYLE)
        form.addWidget(lbl, row, 0)
        form.addWidget(inp, row, 1)
        if attr:
            setattr(self, attr, inp)
        else:
            setattr(self, label_text.lower().replace(" ", "_") + "_inp", inp)
        return inp

    def _pick_color(self):
        color = QColorDialog.getColor(self.variant_color, self, "Pick Variant Color")
        if color.isValid():
            self.variant_color = color
            self.variant_swatch.setStyleSheet(
                f"background:{color.name()}; border:1px solid #888;"
            )

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.image_path = path
            pix = QPixmap(path).scaled(150, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_preview.setPixmap(pix)

    def _save(self):
        name  = self.dinosaur_inp.text().strip()
        gene  = self.gene_cb.currentText()
        price_str = self.price_inp.text().replace("$", "").replace(",", "").strip()
        gender = self.gender_cb.currentText()

        try:
            price = float(price_str)
        except ValueError:
            price = 0.0

        if not name:
            print("Dinosaur name is required!")
            return

        self.stock_data.append({
            "name":          name,
            "gene":          gene,
            "price":         price,
            "gender":        gender,
            "variant_color": QColor(self.variant_color),
            "image_path":    self.image_path,
        })
        self.stock_page.refresh()
        print(f"Added: {name} ({gene}) ${price:,.0f}")

        # reset form
        self.dinosaur_inp.clear()
        self.price_inp.setText("$25,000,000")
        self.image_path = ""
        self.img_preview.setPixmap(QPixmap())
        self.img_preview.setStyleSheet("QLabel { background: #c8c8c8; border-radius: 10px; }")


# ════════════════════════ StorePage ═════════════════════════════
class StorePage(QWidget):
    """
    Drop-in central widget.
    Contains: Store Profile | Stock | Add Stock tabs.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # shared mutable list so Stock and AddStock stay in sync
        self._stock_data = [
            {"name": "Tyrannosaurus Rex",  "gene": "Carnivore", "price": 25_000_000,
             "gender": "Female", "variant_color": QColor("#2e7d32"), "image_path": ""},
            {"name": "Phuwiangosaurus",    "gene": "Herbivore", "price": 50_000_000,
             "gender": "Female", "variant_color": QColor("#f9a825"), "image_path": ""},
            {"name": "Aptonoth",           "gene": "Herbivore", "price": 15_000_000,
             "gender": "Male",   "variant_color": QColor("#6d4c41"), "image_path": ""},
        ]
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.setSpacing(0)

        # card
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

        # tab bar
        tab_bar = QWidget()
        tab_bar.setStyleSheet("background: transparent;")
        tb_lay = QHBoxLayout(tab_bar)
        tb_lay.setContentsMargins(0, 0, 0, 0)
        tb_lay.setSpacing(0)

        self.tab_profile  = make_tab_btn("Store Profile")
        self.tab_stock    = make_tab_btn("Stock")
        self.tab_addstock = make_tab_btn("Add stock")
        self.tabs = [self.tab_profile, self.tab_stock, self.tab_addstock]

        tb_lay.addWidget(self.tab_profile)
        tb_lay.addWidget(self.tab_stock)
        tb_lay.addWidget(self.tab_addstock)
        tb_lay.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #cccccc;")

        # pages
        self.stack = QStackedWidget()

        self.page_profile  = StoreProfilePage()
        self.page_stock    = StockPage(self._stock_data)
        self.page_addstock = AddStockPage(self._stock_data, self.page_stock)

        self.stack.addWidget(self.page_profile)
        self.stack.addWidget(self.page_stock)
        self.stack.addWidget(self.page_addstock)

        card_layout.addWidget(tab_bar)
        card_layout.addWidget(sep)
        card_layout.addWidget(self.stack)

        outer.addWidget(card)

        # connect
        self.tab_profile.clicked.connect(lambda: self._switch(0))
        self.tab_stock.clicked.connect(lambda: self._switch(1))
        self.tab_addstock.clicked.connect(lambda: self._switch(2))

        self._switch(0)

    def _switch(self, index: int):
        self.stack.setCurrentIndex(index)
        apply_tab_styles(self.tabs, index)