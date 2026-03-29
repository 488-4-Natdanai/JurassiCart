import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QLabel, QLineEdit, QDateEdit,
    QSpinBox, QPushButton, QDialog, QMessageBox, QScrollArea, QFrame, QSizePolicy,
    QToolBar, QTabWidget, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QColorDialog)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon, QColor

dir = os.path.dirname(os.path.abspath(__file__))
dino_logo   = os.path.join(dir, "resorces", "dino2.png")
juras_logo  = os.path.join(dir, "resorces", "JurassiLogo.png")

# ── shared style helpers ────────────────────────────────────────────────────────
BTN_GREEN = """
    QPushButton {
        background:#0b7a12; color:white; border-radius:14px;
        font-size:14px; font-weight:bold; padding:6px 20px;
    }
    QPushButton:hover { background:#0d9918; }
    QPushButton:pressed { background:#085c0d; }
"""
BTN_GREY = """
    QPushButton {
        background:#d0d0d0; color:#333; border-radius:14px;
        font-size:14px; padding:6px 20px;
    }
    QPushButton:hover { background:#bbbbbb; }
"""
INPUT_STYLE = """
    QLineEdit, QComboBox {
        border:1px solid #ccc; border-radius:14px;
        padding:4px 12px; font-size:13px; background:white;
    }
    QComboBox::drop-down { border:none; width:24px; }
"""

# ── colour swatch button ────────────────────────────────────────────────────────
class ColorSwatch(QPushButton):
    """Square button that opens a QColorDialog and shows the chosen colour."""
    def __init__(self, color: QColor = QColor("#1a7a1a"), parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self._color = color
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background:{self._color.name()};
                border:2px solid #888; border-radius:4px;
            }}
            QPushButton:hover {{ border-color:#333; }}
        """)

    def _pick(self):
        c = QColorDialog.getColor(self._color, self, "Pick variant colour")
        if c.isValid():
            self._color = c
            self._refresh()

    def color(self) -> QColor:
        return self._color


# ── image picker label ──────────────────────────────────────────────────────────
class ImagePicker(QWidget):
    """Grey placeholder + 'Select Image' button; shows chosen image."""
    def __init__(self, size=(160, 120), parent=None):
        super().__init__(parent)
        self._path = None
        self._w, self._h = size

        self._img_label = QLabel()
        self._img_label.setFixedSize(self._w, self._h)
        self._img_label.setAlignment(Qt.AlignCenter)
        self._img_label.setStyleSheet(
            "background:#d0d0d0; border-radius:8px; color:#888; font-size:12px;")
        self._img_label.setText("No image")

        self._btn = QPushButton("Select Image")
        self._btn.setStyleSheet(BTN_GREY)
        self._btn.clicked.connect(self._select)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self._img_label)
        lay.addWidget(self._btn, alignment=Qt.AlignHCenter)

    def _select(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            self._path  = path
            pix = QPixmap(path).scaled(
                self._w, self._h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._img_label.setPixmap(pix)
            self._img_label.setText("")

    def clear(self):
        self._path = None
        self._img_label.setPixmap(QPixmap())
        self._img_label.setText("No image")

    def path(self):
        return self._path


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 – Store Profile
# ══════════════════════════════════════════════════════════════════════════════
class StoreProfileTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(60)

        # ── left: form ──────────────────────────────────────────────────────
        form_widget = QWidget()
        form_lay    = QFormLayout(form_widget)
        form_lay.setSpacing(16)
        form_lay.setLabelAlignment(Qt.AlignRight)

        name_label = QLabel("Store name")
        name_label.setFont(QFont("", 12))

        self.store_name_edit = QLineEdit()
        self.store_name_edit.setText("Jane Doe")
        self.store_name_edit.setFixedWidth(200)
        self.store_name_edit.setStyleSheet(INPUT_STYLE)

        form_lay.addRow(name_label, self.store_name_edit)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BTN_GREEN)
        save_btn.setFixedWidth(100)
        save_btn.clicked.connect(self._save)
        form_lay.addRow("", save_btn)

        root.addWidget(form_widget, alignment=Qt.AlignTop)

        # ── right: profile picture ──────────────────────────────────────────
        self._avatar = ImagePicker(size=(120, 120))
        root.addWidget(self._avatar, alignment=Qt.AlignTop)
        root.addStretch()

    def _save(self):
        QMessageBox.information(self, "Saved", "Store profile saved successfully!")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – Stock
# ══════════════════════════════════════════════════════════════════════════════
class StockTab(QWidget):
    """Lists all dinos currently for sale. Receives a reference to the shared
    stock list so it can stay in sync when Add-stock saves a new entry."""

    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data   # shared list of dicts
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 20, 30, 20)

        self._table = QTableWidget()
        self._table.setColumnCount(5)           # #, image, name/type, price, delete
        self._table.setHorizontalHeaderLabels(["", "", "Name", "Price", ""])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.horizontalHeader().setVisible(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.setStyleSheet("""
            QTableWidget { background:transparent; border:none; }
            QTableWidget::item { padding:8px; border-bottom:1px solid #e0e0e0; }
        """)

        lay.addWidget(self._table)
        self.refresh()

    def refresh(self):
        self._table.setRowCount(0)
        for i, item in enumerate(self._data):
            self._table.insertRow(i)
            self._table.setRowHeight(i, 70)

            # col 0 – row number
            num = QTableWidgetItem(str(i + 1))
            num.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(i, 0, num)
            self._table.setColumnWidth(0, 40)

            # col 1 – dino image (thumbnail) or placeholder
            img_label = QLabel()
            img_label.setFixedSize(50, 50)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setStyleSheet("background:#d0d0d0; border-radius:6px;")
            if item.get("image"):
                pix = QPixmap(item["image"]).scaled(
                    50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(pix)
            else:
                img_label.setText("🦕")
                img_label.setFont(QFont("", 20))
            self._table.setCellWidget(i, 1, img_label)
            self._table.setColumnWidth(1, 70)

            # col 2 – name, type, variant colour swatch
            info_widget = QWidget()
            info_lay    = QVBoxLayout(info_widget)
            info_lay.setContentsMargins(4, 4, 4, 4)
            info_lay.setSpacing(2)

            name_lbl = QLabel(item["name"])
            name_lbl.setFont(QFont("", 11, QFont.Bold))
            type_lbl = QLabel(item["gene"])
            type_lbl.setFont(QFont("", 9))
            type_lbl.setStyleSheet("color:#666;")

            swatch = QLabel()
            swatch.setFixedSize(16, 16)
            swatch.setStyleSheet(
                f"background:{item['color']}; border-radius:3px; border:1px solid #aaa;")

            variant_row = QHBoxLayout()
            variant_row.setSpacing(4)
            variant_lbl = QLabel("Variant")
            variant_lbl.setStyleSheet("color:#666; font-size:9px;")
            variant_row.addWidget(variant_lbl)
            variant_row.addWidget(swatch)
            variant_row.addStretch()

            info_lay.addWidget(name_lbl)
            info_lay.addWidget(type_lbl)
            info_lay.addLayout(variant_row)
            self._table.setCellWidget(i, 2, info_widget)

            # col 3 – price
            price = QTableWidgetItem(item["price"])
            price.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(i, 3, price)
            self._table.setColumnWidth(3, 130)

            # col 4 – delete button
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet(BTN_GREY)
            del_btn.clicked.connect(lambda _, idx=i: self._delete(idx))
            self._table.setCellWidget(i, 4, del_btn)
            self._table.setColumnWidth(4, 100)

    def _delete(self, idx: int):
        name = self._data[idx]["name"]
        reply = QMessageBox.question(
            self, "Delete", f"Remove {name} from stock?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._data.pop(idx)
            self.refresh()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – Add Stock
# ══════════════════════════════════════════════════════════════════════════════
class AddStockTab(QWidget):
    item_added = Signal()   # emitted after save so StockTab can refresh

    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(50)

        # ── left: form ──────────────────────────────────────────────────────
        form_widget = QWidget()
        form_lay    = QFormLayout(form_widget)
        form_lay.setSpacing(14)
        form_lay.setLabelAlignment(Qt.AlignRight)

        def make_label(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("", 11))
            return lbl

        # Dinosaur name
        self.dino_edit = QLineEdit()
        self.dino_edit.setPlaceholderText("e.g. Tyrannosaurus Rex")
        self.dino_edit.setFixedWidth(200)
        self.dino_edit.setStyleSheet(INPUT_STYLE)
        form_lay.addRow(make_label("Dinosaur"), self.dino_edit)

        # Gene (type)
        self.gene_combo = QComboBox()
        self.gene_combo.addItems(["Carnivore", "Herbivore", "Omnivore"])
        self.gene_combo.setFixedWidth(200)
        self.gene_combo.setStyleSheet(INPUT_STYLE)
        form_lay.addRow(make_label("Gene"), self.gene_combo)

        # Price
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("e.g. $25,000,000")
        self.price_edit.setFixedWidth(200)
        self.price_edit.setStyleSheet(INPUT_STYLE)
        form_lay.addRow(make_label("Price"), self.price_edit)

        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Female", "Male"])
        self.gender_combo.setFixedWidth(200)
        self.gender_combo.setStyleSheet(INPUT_STYLE)
        form_lay.addRow(make_label("Gender"), self.gender_combo)

        # Variant colour
        self._swatch = ColorSwatch(QColor("#1a7a1a"))
        form_lay.addRow(make_label("Variant"), self._swatch)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BTN_GREEN)
        save_btn.setFixedWidth(100)
        save_btn.clicked.connect(self._save)
        form_lay.addRow("", save_btn)

        root.addWidget(form_widget, alignment=Qt.AlignTop)

        # ── right: image picker ─────────────────────────────────────────────
        self._img_picker = ImagePicker(size=(160, 130))
        root.addWidget(self._img_picker, alignment=Qt.AlignTop)
        root.addStretch()

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

        QMessageBox.information(self, "Saved", f"{name} has been added to your stock!")
        self.item_added.emit()
        self._clear_form()

    def _clear_form(self):
        self.dino_edit.clear()
        self.price_edit.clear()
        self.gene_combo.setCurrentIndex(0)
        self.gender_combo.setCurrentIndex(0)
        self._swatch._color = QColor("#1a7a1a")
        self._swatch._refresh()
        self._img_picker.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  Main stock widget (tab container)
# ══════════════════════════════════════════════════════════════════════════════
class stock(QWidget):
    def __init__(self):
        super().__init__()
        self._stock_data = []   # shared list passed to both tabs
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── tab widget ──────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border:1px solid #ccc; border-radius:8px;
                background:white; margin-top:-1px;
            }
            QTabBar::tab {
                padding:10px 28px; font-size:13px;
                background:#e8e8e8; border:1px solid #ccc;
                border-bottom:none; border-top-left-radius:6px;
                border-top-right-radius:6px; margin-right:2px;
            }
            QTabBar::tab:selected {
                background:white; font-weight:bold;
            }
            QTabBar::tab:hover:!selected { background:#d4d4d4; }
        """)

        self._profile_tab  = StoreProfileTab()
        self._stock_tab    = StockTab(self._stock_data)
        self._addstock_tab = AddStockTab(self._stock_data)

        # when a new item is saved, refresh the stock list tab
        self._addstock_tab.item_added.connect(self._stock_tab.refresh)

        self.tabs.addTab(self._profile_tab,  "Store Profile")
        self.tabs.addTab(self._stock_tab,    "Stock")
        self.tabs.addTab(self._addstock_tab, "Add stock")

        layout.addWidget(self.tabs)


# ══════════════════════════════════════════════════════════════════════════════
#  Main window (unchanged except it now gets a real stock widget)
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
                             ("Stock",        lambda: print("go stock")),
                             ("Add stock",    lambda: print("go add_stock"))]:
            a = QAction(label, self)
            a.triggered.connect(slot)
            store_menu.addAction(a)

        acc_menu = self.menuBar().addMenu("Account")
        for label, slot in [("My account", lambda: print("my account")),
                             ("My Cart",   lambda: print("go cart"))]:
            a = QAction(label, self)
            a.triggered.connect(slot)
            acc_menu.addAction(a)

    def create_toolbar(self):
        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background:#0b7a12; spacing:10px; padding:8px;
            }
        """)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        icon_style = """
            QPushButton {
                color:white; font-size:40px;
                background:transparent; border:none; padding:5px;
            }
            QPushButton:hover {
                background-color:rgba(255,255,255,0.2); border-radius:20px;
            }
        """

        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40, 40))

        self.name_btn = QPushButton("JurassiCart")
        font_path  = os.path.join(dir, "resorces", "DinopiaRegular-mLrO9.otf")
        font_id    = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.name_btn.setFont(QFont(font_family, 12))
        self.name_btn.setStyleSheet("""
            QPushButton {
                color:white; font-size:30px; font-weight:bold;
                background:transparent; border:none;
            }
            QPushButton:hover { color:#ccffcc; }
        """)

        search_container = QWidget()
        search_container.setStyleSheet(
            "QWidget { background:white; border-radius:20px; }")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 10, 0)
        search_layout.setSpacing(5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet(
            "QLineEdit { border:none; background:transparent; font-size:14px; }")

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(dir, "resorces", "search.png")))
        search_icon.clicked.connect(lambda: print("Search"))
        search_icon.setFixedSize(44, 44)
        search_icon.setIconSize(QSize(24, 24))
        search_icon.setStyleSheet("""
            QPushButton {
                color:white; font-size:40px;
                background:transparent; border:none; padding:5px;
            }
            QPushButton:hover {
                background-color:#999999; border-radius:22px;
            }
        """)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        self.filter_btn  = QPushButton()
        self.filter_btn.setIcon(QIcon(os.path.join(dir, "resorces", "filter.png")))
        self.filter_btn.setIconSize(QSize(24, 24))
        self.cart_btn    = QPushButton()
        self.cart_btn.setIcon(QIcon(os.path.join(dir, "resorces", "cart.png")))
        self.cart_btn.setIconSize(QSize(40, 40))
        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(os.path.join(dir, "resorces", "user.png")))
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
    app.setWindowIcon(QIcon(dino_logo))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()