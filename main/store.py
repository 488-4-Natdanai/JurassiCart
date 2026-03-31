import os
import database as db
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

        self.store_name = QLineEdit()
        self.store_name.setPlaceholderText("e.g. Jane Doe")
        self.store_name.setFixedWidth(210)
        self.store_name.setFixedHeight(28)
        self.store_name.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bbb;
                border-radius: 12px;
                padding: 2px 12px;
                font-size: 12px;
                background: white;
            }
        """)

        name_row.addWidget(name_lbl)
        name_row.addWidget(self.store_name)
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
        if not self.store_name.text().strip():
            QMessageBox.warning(self, "Invalid", "Please enter a store name.")
            return
        QMessageBox.information(self, "Saved", "Store profile saved successfully!")

    def load_store(self, store: dict):
        self.store_name.setText(store.get("store_name", ""))


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

        vrow = QHBoxLayout()
        vrow.setSpacing(4)
        vl = QLabel("Variant")
        vl.setFont(QFont("", 9))
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
        price = QLabel(f"${item['price']}" if not item['price'].startswith('$') else item['price'])
        price.setFont(QFont("", 11))
        price.setFixedWidth(130)
        price.setAlignment(Qt.AlignCenter)
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
    item_deleted = Signal()   # bubble up to home.refresh

    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data
        self._store_id: str | None = None
        self.setStyleSheet("background: white;")
        self._build_ui()

    def load_store(self, store_id: str):
        self._store_id = store_id
        self.refresh()

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
        # reload from DB if we have a store_id, else use in-memory list
        if self._store_id:
            self._data = db.get_dinosaurs_by_store(self._store_id)

        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._data:
            empty = QLabel("Your stock is empty. Let's add something!")
            empty.setAlignment(Qt.AlignCenter)
            empty.setFont(QFont("", 13))
            self._list_lay.setAlignment(Qt.AlignCenter)
            self._list_lay.addWidget(empty)
            return

        self._list_lay.setAlignment(Qt.AlignTop)
        for i, item in enumerate(self._data):
            row = StockRow(i, item)
            row.delete_requested.connect(self._delete)
            self._list_lay.addWidget(row)

    def _delete(self, idx: int):
        item = self._data[idx]
        name = item["name"]
        reply = QMessageBox.question(
            self, "Delete",
            f"Remove {name} from stock?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self._store_id and item.get("dino_id"):
                db.delete_dinosaur(item["dino_id"])
            self._data.pop(idx)
            self.refresh()
            self.item_deleted.emit()   # notify home to refresh


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – Add Stock
# ══════════════════════════════════════════════════════════════════════════════
class AddStockTab(QWidget):
    item_added = Signal()

    def __init__(self, stock_data: list, parent=None):
        super().__init__(parent)
        self._data = stock_data
        self._store_id: str | None = None   # set by StorePage after login
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

        from PySide6.QtWidgets import QSpinBox
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setStyleSheet(field_style)
        form_vlay.addLayout(make_row("Quantity", self.qty_spin))

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
        cleaned = price.replace(",", "").replace("$", "").strip()
        if not cleaned.isdigit():
            QMessageBox.warning(self, "Invalid price", "Price must be a number.")
            return

        new_item = {
            "name":   name,
            "gene":   self.gene_combo.currentText(),
            "price":  cleaned,
            "gender": self.gender_combo.currentText(),
            "color":  self._swatch.color().name(),
            "image":  self._img_picker.path() or "",
        }

        # save to DB if store_id is set
        if self._store_id:
            # copy image to resorces/ named after the dino
            img_dest = ""
            if new_item["image"] and os.path.exists(new_item["image"]):
                ext = os.path.splitext(new_item["image"])[-1]
                img_dest = os.path.join(dir_path, "resorces", name + ext)
                import shutil
                shutil.copy2(new_item["image"], img_dest)

            db.add_dinosaur(
                store_id=self._store_id,
                name=name,
                gene=new_item["gene"],
                gender=new_item["gender"],
                age=0,
                color=new_item["color"],
                price=int(cleaned),
                stock=self.qty_spin.value(),
                image=img_dest,
            )
        else:
            self._data.append(new_item)

        QMessageBox.information(self, "Saved", f"{name} has been added to your stock!")
        self.item_added.emit()
        self._clear_form()

    def _clear_form(self):
        self.dino_edit.clear()
        self.price_edit.clear()
        self.gene_combo.setCurrentIndex(0)
        self.gender_combo.setCurrentIndex(0)
        self.qty_spin.setValue(1)
        self._swatch.reset()
        self._img_picker.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  Custom tab container matching the screenshot header style exactly
# ══════════════════════════════════════════════════════════════════════════════
class StoreTabWidget(QWidget):
    item_added = Signal()   # bubbles up to MainWindow → home.refresh

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stock_data = []
        self._user = None
        self._build_ui()

    def _on_item_added(self):
        self.item_added.emit()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 20, 40, 20)
        outer.setSpacing(0)

        # White card with border
        card = QFrame()
        card.setObjectName("card")
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame#card {
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
        self._addstock_tab.item_added.connect(self._on_item_added)
        self._stock_tab.item_deleted.connect(self.item_added.emit)  # reuse same signal → home.refresh

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

    def load_user(self, user: dict):
        """Auto-create store if needed, then wire store_id to all tabs."""
        self._user = user
        store = db.get_store_by_user(user["user_id"])
        if not store:
            # auto-create store named after username
            store = db.create_store(
                user["user_id"],
                store_name=f"{user['username']}'s Store",
            )
        store_id = store["store_id"]
        self._addstock_tab._store_id = store_id
        self._profile_tab.load_store(store)
        self._stock_tab.load_store(store_id)


# ══════════════════════════════════════════════════════════════════════════════
#  Central widget
# ══════════════════════════════════════════════════════════════════════════════
class StorePage(QWidget):
    item_added = Signal()   # forward to MainWindow

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #ebebeb;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._tab_widget = StoreTabWidget()
        self._tab_widget.item_added.connect(self.item_added.emit)
        lay.addWidget(self._tab_widget)

    def load_user(self, user: dict):
        self._tab_widget.load_user(user)

