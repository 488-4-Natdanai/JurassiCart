import sys, os
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QSpinBox, QPushButton,
    QDialog, QMessageBox, QScrollArea, QFrame, QSizePolicy,
    QToolBar, QComboBox, QFileDialog, QColorDialog
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon, QColor

dir_path   = os.path.dirname(os.path.abspath(__file__))
dino_logo  = os.path.join(dir_path, "resorces", "dino2.png")
juras_logo = os.path.join(dir_path, "resorces", "JurassiLogo.png")


# ── colour swatch button ──────────────────────────────────────────────────────
class ColorSwatch(QPushButton):
    def __init__(self, color: QColor = QColor("#1a7a1a"), parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self._color = color
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color.name()};
                border: 1px solid #555;
                border-radius: 3px;
            }}
        """)

    def _pick(self):
        c = QColorDialog.getColor(self._color, self, "Pick variant colour")
        if c.isValid():
            self._color = c
            self._refresh()

    def color(self) -> QColor:
        return self._color

    def reset(self):
        self._color = QColor("#1a7a1a")
        self._refresh()


# ── image picker widget ───────────────────────────────────────────────────────
class ImagePicker(QWidget):
    def __init__(self, placeholder_size=(160, 120), circular=False, parent=None):
        super().__init__(parent)
        self._path = None
        self._w, self._h = placeholder_size
        self._circular   = circular

        self._img_label = QLabel()
        self._img_label.setFixedSize(self._w, self._h)
        self._img_label.setAlignment(Qt.AlignCenter)
        radius = self._w // 2 if circular else 8
        self._img_label.setStyleSheet(
            f"background: #c0c0c0; border-radius: {radius}px;")

        self._btn = QPushButton("Select Image")
        self._btn.setStyleSheet("""
            QPushButton {
                background: #e0e0e0;
                border: 1px solid #bbb;
                border-radius: 12px;
                font-size: 12px;
                padding: 4px 14px;
                color: #333;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        self._btn.clicked.connect(self._select)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        lay.addWidget(self._img_label, alignment=Qt.AlignHCenter)
        lay.addWidget(self._btn,       alignment=Qt.AlignHCenter)

    def _select(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            self._path = path
            pix = QPixmap(path).scaled(
                self._w, self._h,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._img_label.setPixmap(pix)

    def clear(self):
        self._path = None
        self._img_label.setPixmap(QPixmap())

    def path(self):
        return self._path


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 – Store Profile
# ══════════════════════════════════════════════════════════════════════════════
class StoreProfileTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(60, 50, 60, 50)
        root.setSpacing(0)

        # ── left: form ──────────────────────────────────────────────────────
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(22)
        left_lay.setAlignment(Qt.AlignTop)

        name_row = QHBoxLayout()
        name_row.setSpacing(12)

        name_lbl = QLabel("Store name")
        name_lbl.setFixedWidth(90)
        name_lbl.setFont(QFont("", 11))
        name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        name_lbl.setStyleSheet("")

        self.store_name_edit = QLineEdit()
        self.store_name_edit.setText("Jane Doe")
        self.store_name_edit.setFixedWidth(210)
        self.store_name_edit.setFixedHeight(28)
        self.store_name_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bbb;
                border-radius: 12px;
                padding: 2px 12px;
                font-size: 12px;
                background: white;
            }
        """)

        name_row.addWidget(name_lbl)
        name_row.addWidget(self.store_name_edit)
        name_row.addStretch()
        left_lay.addLayout(name_row)

        # Save button aligned under the input
        save_row = QHBoxLayout()
        pad = QWidget(); pad.setFixedWidth(102)
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(90, 32)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #0b7a12; color: white;
                border-radius: 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover   { background: #0d9918; }
            QPushButton:pressed { background: #085c0d; }
        """)
        save_btn.clicked.connect(self._save)
        save_row.addWidget(pad)
        save_row.addWidget(save_btn)
        save_row.addStretch()
        left_lay.addLayout(save_row)
        left_lay.addStretch()

        root.addWidget(left, stretch=1)

        # ── vertical divider ────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color: #ddd;")
        root.addWidget(line)

        # ── right: profile image picker ─────────────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(40, 10, 0, 0)
        right_lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self._avatar = ImagePicker(placeholder_size=(90, 90), circular=True)
        right_lay.addWidget(self._avatar)
        right_lay.addStretch()
        root.addWidget(right, stretch=1)

    def _save(self):
        QMessageBox.information(self, "Saved", "Store profile saved successfully!")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – Stock  (individual row widget)
# ══════════════════════════════════════════════════════════════════════════════
class StockRow(QWidget):
    delete_requested = Signal(int)

    def __init__(self, index: int, item: dict, parent=None):
        super().__init__(parent)
        self._index = index
        self.setFixedHeight(68)
        self.setStyleSheet("background: #d8d8d8; border-radius: 6px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(10)

        # index number
        num = QLabel(str(index + 1))
        num.setFixedWidth(24)
        num.setAlignment(Qt.AlignCenter)
        num.setFont(QFont("", 11))
        num.setStyleSheet("")
        lay.addWidget(num)

        # thumbnail
        thumb = QLabel()
        thumb.setFixedSize(48, 48)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("background: #b8b8b8; border-radius: 4px;")
        if item.get("image"):
            pix = QPixmap(item["image"]).scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(pix)
        else:
            thumb.setText("🦕")
            thumb.setFont(QFont("", 18))
        lay.addWidget(thumb)

        # name / type / variant
        info = QWidget()
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(4, 0, 0, 0)
        info_lay.setSpacing(1)

        n = QLabel(item["name"])
        n.setFont(QFont("", 11, QFont.Bold))

        t = QLabel(item["gene"])
        t.setFont(QFont("", 9))
        t.setStyleSheet("color: #555;")

        vrow = QHBoxLayout()
        vrow.setSpacing(4)
        vl = QLabel("Variant")
        vl.setFont(QFont("", 9))
        vl.setStyleSheet("color: #555;")
        sw = QLabel()
        sw.setFixedSize(14, 14)
        sw.setStyleSheet(
            f"background: {item['color']}; border-radius: 2px;"
            " border: 1px solid #777;")
        vrow.addWidget(vl)
        vrow.addWidget(sw)
        vrow.addStretch()

        info_lay.addWidget(n)
        info_lay.addWidget(t)
        info_lay.addLayout(vrow)
        lay.addWidget(info, stretch=1)

        # price
        price = QLabel(item["price"])
        price.setFont(QFont("", 11))
        price.setFixedWidth(130)
        price.setAlignment(Qt.AlignCenter)
        price.setStyleSheet("")
        lay.addWidget(price)

        # delete button
        del_btn = QPushButton("Delete")
        del_btn.setFixedSize(74, 30)
        del_btn.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; border: 1px solid #bbb;
                border-radius: 14px; font-size: 12px; color: #333;
            }
            QPushButton:hover   { background: #cccccc; }
            QPushButton:pressed { background: #b0b0b0; }
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._index))
        lay.addWidget(del_btn)


class StockTab(QWidget):
    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data
        self.setStyleSheet("background: white;")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background: white;")

        self._container = QWidget()
        self._container.setStyleSheet("background: white;")
        self._list_lay = QVBoxLayout(self._container)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(8)
        self._list_lay.setAlignment(Qt.AlignTop)

        self._scroll.setWidget(self._container)
        outer.addWidget(self._scroll)
        self.refresh()

    def refresh(self):
        # clear
        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._data:
            empty = QLabel("Your stock is empty, Let's add something!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setFont(QFont("", 13))
            empty.setStyleSheet("color: #888;")
            self._list_lay.setAlignment(Qt.AlignCenter)
            self._list_lay.addWidget(empty)
            return

        self._list_lay.setAlignment(Qt.AlignTop)
        for i, item in enumerate(self._data):
            row = StockRow(i, item)
            row.delete_requested.connect(self._delete)
            self._list_lay.addWidget(row)

    def _delete(self, idx: int):
        name = self._data[idx]["name"]
        reply = QMessageBox.question(
            self, "Delete",
            f"Remove {name} from stock?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._data.pop(idx)
            self.refresh()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – Add Stock
# ══════════════════════════════════════════════════════════════════════════════
class AddStockTab(QWidget):
    item_added = Signal()

    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data
        self.setStyleSheet("background: white;")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(60, 50, 60, 50)
        root.setSpacing(0)

        # ── left: form ──────────────────────────────────────────────────────
        form_w = QWidget()
        form_vlay = QVBoxLayout(form_w)
        form_vlay.setContentsMargins(0, 0, 0, 0)
        form_vlay.setSpacing(14)
        form_vlay.setAlignment(Qt.AlignTop)

        LABEL_W = 70
        field_style = """
            QLineEdit, QComboBox {
                border: 1px solid #bbb;
                border-radius: 12px;
                padding: 3px 12px;
                font-size: 12px;
                background: white;
                min-width: 200px;
                max-width: 210px;
                height: 26px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
        """

        def make_row(label_text, widget):
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("", 11))
            lbl.setFixedWidth(LABEL_W)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            return row

        self.dino_edit = QLineEdit()
        self.dino_edit.setPlaceholderText("e.g. Tyrannosaurus Rex")
        self.dino_edit.setStyleSheet(field_style)
        form_vlay.addLayout(make_row("Dinosaur", self.dino_edit))

        self.gene_combo = QComboBox()
        self.gene_combo.addItems(["Carnivore", "Herbivore", "Omnivore"])
        self.gene_combo.setStyleSheet(field_style)
        form_vlay.addLayout(make_row("Gene", self.gene_combo))

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("e.g. $25,000,000")
        self.price_edit.setStyleSheet(field_style)
        form_vlay.addLayout(make_row("Price", self.price_edit))

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Female", "Male"])
        self.gender_combo.setStyleSheet(field_style)
        form_vlay.addLayout(make_row("Gender", self.gender_combo))

        self._swatch = ColorSwatch(QColor("#1a7a1a"))
        form_vlay.addLayout(make_row("Variant", self._swatch))

        # Save button indented to align with fields
        save_row = QHBoxLayout()
        save_row.setSpacing(12)
        save_pad = QWidget(); save_pad.setFixedWidth(LABEL_W + 12)
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(90, 32)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #0b7a12; color: white;
                border-radius: 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover   { background: #0d9918; }
            QPushButton:pressed { background: #085c0d; }
        """)
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_pad)
        save_row.addWidget(save_btn)
        save_row.addStretch()
        form_vlay.addLayout(save_row)

        root.addWidget(form_w, stretch=1)

        # ── vertical divider ────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color: #ddd;")
        root.addWidget(line)

        # ── right: image picker ─────────────────────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(40, 10, 0, 0)
        right_lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self._img_picker = ImagePicker(placeholder_size=(180, 140), circular=False)
        right_lay.addWidget(self._img_picker)
        right_lay.addStretch()
        root.addWidget(right, stretch=1)

    def _save(self):
        name  = self.dino_edit.text().strip()
        price = self.price_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing field", "Please enter a dinosaur name.")
            return
        if not price:
            QMessageBox.warning(self, "Missing field", "Please enter a price.")
            return

        self._data.append({
            "name":   name,
            "gene":   self.gene_combo.currentText(),
            "price":  price,
            "gender": self.gender_combo.currentText(),
            "color":  self._swatch.color().name(),
            "image":  self._img_picker.path(),
        })
        QMessageBox.information(self, "Saved",
                                f"{name} has been added to your stock!")
        self.item_added.emit()
        self._clear_form()

    def _clear_form(self):
        self.dino_edit.clear()
        self.price_edit.clear()
        self.gene_combo.setCurrentIndex(0)
        self.gender_combo.setCurrentIndex(0)
        self._swatch.reset()
        self._img_picker.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  Custom tab container matching the screenshot header style exactly
# ══════════════════════════════════════════════════════════════════════════════
class StoreTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stock_data = []
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 20, 40, 20)
        outer.setSpacing(0)

        # White card with border
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #c8c8c8;
                border-radius: 4px;
            }
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        # ── tab header ──────────────────────────────────────────────────────
        tab_bar = QWidget()
        tab_bar.setFixedHeight(54)
        tab_bar.setStyleSheet("background: transparent; border: none;")
        tab_bar_lay = QHBoxLayout(tab_bar)
        tab_bar_lay.setContentsMargins(0, 0, 0, 0)
        tab_bar_lay.setSpacing(0)

        self._tab_btns = []
        for i, name in enumerate(["Store Profile", "Stock", "Add stock"]):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("", 12))
            btn.setStyleSheet(self._tab_style(False))
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            self._tab_btns.append(btn)
            tab_bar_lay.addWidget(btn)

        tab_bar_lay.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #c8c8c8; border: none;")

        card_lay.addWidget(tab_bar)
        card_lay.addWidget(sep)

        # ── stacked pages ───────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: white;")

        self._profile_tab  = StoreProfileTab()
        self._stock_tab    = StockTab(self._stock_data)
        self._addstock_tab = AddStockTab(self._stock_data)
        self._addstock_tab.item_added.connect(self._stock_tab.refresh)

        self._stack.addWidget(self._profile_tab)
        self._stack.addWidget(self._stock_tab)
        self._stack.addWidget(self._addstock_tab)

        card_lay.addWidget(self._stack)
        outer.addWidget(card)

        self._switch(0)

    @staticmethod
    def _tab_style(selected: bool) -> str:
        if selected:
            return """
                QPushButton {
                    background: white;
                    border: none;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 12px 32px;
                    color: #111;
                }
            """
        return """
            QPushButton {
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: normal;
                padding: 12px 32px;
                color: #555;
            }
            QPushButton:hover { color: #111; }
        """

    def _switch(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_btns):
            btn.setChecked(i == idx)
            btn.setStyleSheet(self._tab_style(i == idx))


# ══════════════════════════════════════════════════════════════════════════════
#  Central widget
# ══════════════════════════════════════════════════════════════════════════════
class stock(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #ebebeb;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(StoreTabWidget())


# ══════════════════════════════════════════════════════════════════════════════
#  Main Window  (toolbar unchanged from original)
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()
        self.setCentralWidget(stock())

    def create_menu(self):
        edit_menu = self.menuBar().addMenu("Edit")
        gen = QAction("Quit", self); gen.triggered.connect(sys.exit)
        edit_menu.addAction(gen)

        nav_menu = self.menuBar().addMenu("Navigation")
        for label, fn in [("Go back",    lambda: print("go back")),
                           ("Go forward", lambda: print("go forward")),
                           ("Home",       lambda: print("go home"))]:
            a = QAction(label, self); a.triggered.connect(fn)
            nav_menu.addAction(a)

        store_menu = self.menuBar().addMenu("Store")
        for label, fn in [("Create store", lambda: print("create store")),
                           ("Stock",        lambda: print("go stock")),
                           ("Add stock",    lambda: print("go add_stock"))]:
            a = QAction(label, self); a.triggered.connect(fn)
            store_menu.addAction(a)

        acc_menu = self.menuBar().addMenu("Account")
        for label, fn in [("My account", lambda: print("my account")),
                           ("My Cart",   lambda: print("go cart"))]:
            a = QAction(label, self); a.triggered.connect(fn)
            acc_menu.addAction(a)

    def create_toolbar(self):
        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet(
            "QToolBar { background:#0b7a12; spacing:10px; padding:8px; }")

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

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

        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40, 40))

        self.name_btn = QPushButton("JurassiCart")
        font_path    = os.path.join(dir_path, "resorces", "DinopiaRegular-mLrO9.otf")
        font_id      = QFontDatabase.addApplicationFont(font_path)
        font_family  = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.name_btn.setFont(QFont(font_family, 12))
        self.name_btn.setStyleSheet("""
            QPushButton {
                color: white; font-size: 30px; font-weight: bold;
                background: transparent; border: none;
            }
            QPushButton:hover { color: #ccffcc; }
        """)

        search_container = QWidget()
        search_container.setStyleSheet(
            "QWidget { background: white; border-radius: 20px; }")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 10, 0)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet(
            "QLineEdit { border:none; background:transparent; font-size:14px; }")

        search_icon = QPushButton()
        search_icon.setIcon(
            QIcon(os.path.join(dir_path, "resorces", "search.png")))
        search_icon.clicked.connect(lambda: print("Search"))
        search_icon.setFixedSize(44, 44)
        search_icon.setIconSize(QSize(24, 24))
        search_icon.setStyleSheet("""
            QPushButton {
                color: white; background: transparent; border: none; padding: 5px;
            }
            QPushButton:hover {
                background-color: #999999; border-radius: 22px;
            }
        """)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        self.filter_btn = QPushButton()
        self.filter_btn.setIcon(
            QIcon(os.path.join(dir_path, "resorces", "filter.png")))
        self.filter_btn.setIconSize(QSize(24, 24))

        self.cart_btn = QPushButton()
        self.cart_btn.setIcon(
            QIcon(os.path.join(dir_path, "resorces", "cart.png")))
        self.cart_btn.setIconSize(QSize(40, 40))

        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(
            QIcon(os.path.join(dir_path, "resorces", "user.png")))
        self.profile_btn.setIconSize(QSize(40, 40))

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
    app.setStyleSheet("QLabel { border: none; background: transparent; }")
    app.setWindowIcon(QIcon(dino_logo))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
