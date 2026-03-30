import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QColor

import database as db

_dir = os.path.dirname(os.path.abspath(__file__))
_dino_placeholder = os.path.join(_dir, "resorces", "dino2.png")


# ── single dino card ─────────────────────────────────────────────────────────
class DinoCard(QFrame):
    add_to_cart = Signal(dict)   # emits dino dict

    def __init__(self, dino: dict, parent=None):
        super().__init__(parent)
        self.dino = dino
        self.setFixedSize(260, 300)
        self.setStyleSheet("""
            DinoCard {
                background: white;
                border-radius: 12px;
            }
            DinoCard:hover {
                background: #f5fff5;
            }
        """)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        """Build the card layout with image, name, meta info, and add-to-cart button."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 14)
        lay.setSpacing(0)

        # image area
        img_lbl = QLabel()
        img_lbl.setFixedSize(260, 160)
        img_lbl.setAlignment(Qt.AlignCenter)
        img_lbl.setStyleSheet("background:#e8e8e8; border-radius:12px 12px 0 0;")

        img_path = self.dino.get("image", "")
        px = QPixmap(img_path) if img_path and os.path.exists(img_path) else QPixmap(_dino_placeholder)
        if not px.isNull():
            img_lbl.setPixmap(px.scaled(260, 160, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            img_lbl.setText("🦕")
            img_lbl.setFont(QFont("Segoe UI", 40))
        lay.addWidget(img_lbl)

        # info area
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(12, 8, 12, 0)
        info_lay.setSpacing(3)

        name_lbl = QLabel(self.dino["name"])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color:#111;")
        name_lbl.setWordWrap(True)
        info_lay.addWidget(name_lbl)

        # gene + variant row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        gene_lbl = QLabel(self.dino.get("gene", ""))
        gene_lbl.setFont(QFont("Segoe UI", 9))
        gene_lbl.setStyleSheet("color:#666;")
        meta_row.addWidget(gene_lbl)

        swatch = QLabel()
        swatch.setFixedSize(12, 12)
        swatch.setStyleSheet(f"background:{self.dino.get('color','#888')};border-radius:2px;")
        meta_row.addWidget(swatch)
        meta_row.addStretch()

        stock = int(self.dino.get("stock", 0))
        stock_lbl = QLabel(f"Stock: {stock}")
        stock_lbl.setFont(QFont("Segoe UI", 9))
        stock_lbl.setStyleSheet(f"color:{'#0b7a12' if stock > 0 else '#cc0000'};")
        meta_row.addWidget(stock_lbl)
        info_lay.addLayout(meta_row)

        # seller label
        store_name = self.dino.get("store_name", "")
        if store_name:
            seller_lbl = QLabel(f"By {store_name}")
            seller_lbl.setFont(QFont("Segoe UI", 8))
            seller_lbl.setStyleSheet("color:#888;")
            info_lay.addWidget(seller_lbl)

        # price + button row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        price_lbl = QLabel(f"${int(self.dino['price']):,}")
        price_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        price_lbl.setStyleSheet("color:#0b7a12;")
        bottom_row.addWidget(price_lbl)
        bottom_row.addStretch()

        add_btn = QPushButton("+ Cart")
        add_btn.setFixedSize(72, 28)
        add_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        add_btn.setStyleSheet("""
            QPushButton{background:#0b7a12;color:white;border:none;border-radius:8px;}
            QPushButton:hover{background:#095e0e;}
            QPushButton:disabled{background:#aaa;}
        """)
        add_btn.setEnabled(stock > 0)
        add_btn.clicked.connect(lambda: self.add_to_cart.emit(self.dino))
        bottom_row.addWidget(add_btn)
        info_lay.addLayout(bottom_row)

        lay.addWidget(info, stretch=1)


# ── home page ────────────────────────────────────────────────────────────────
class home(QWidget):
    add_to_cart = Signal(dict)   # bubbles up to MainWindow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#f0f0f0;")
        self._build_ui()

    def _build_ui(self):
        """Build the scrollable grid layout for the home page."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel("All Dinosaurs")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color:#111;")
        title_row.addWidget(title)
        title_row.addStretch()
        outer.addLayout(title_row)

        from PySide6.QtWidgets import QStackedWidget
        self._stack = QStackedWidget()

        # page 0 — grid of cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;")
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background:transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(20)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self._grid_widget)
        self._stack.addWidget(scroll)   # index 0

        # page 1 — empty/no-results message
        self._empty_lbl = QLabel()
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setFont(QFont("Segoe UI", 13))
        self._empty_lbl.setStyleSheet("color:#888;")
        self._stack.addWidget(self._empty_lbl)   # index 1

        outer.addWidget(self._stack, stretch=1)
        self.refresh()

    def refresh(self, gene_filter: str = "", search: str = ""):
        """Reload dino cards from the database, applying optional filter and search."""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        dinos = db.get_all_dinosaurs()

        if gene_filter:
            dinos = [d for d in dinos if d.get("gene", "").lower() == gene_filter.lower()]

        q = search.strip().lower()
        if q:
            dinos = [d for d in dinos if q in d["name"].lower()]

        # newest first; out-of-stock goes to bottom
        dinos.sort(key=lambda d: (int(d.get("stock", 0)) == 0, d.get("created_at", "")), reverse=False)
        in_stock  = sorted([d for d in dinos if int(d.get("stock", 0)) > 0],
                           key=lambda d: d.get("created_at", ""), reverse=True)
        out_stock = sorted([d for d in dinos if int(d.get("stock", 0)) == 0],
                           key=lambda d: d.get("created_at", ""), reverse=True)
        dinos = in_stock + out_stock

        if not dinos:
            msg = "No results found."
            if q:
                msg += "\nDouble-check your spelling — there might be a typo."
            self._empty_lbl.setText(msg)
            self._stack.setCurrentIndex(1)
            return

        self._stack.setCurrentIndex(0)
        COLS = 4
        for i, dino in enumerate(dinos):
            card = DinoCard(dino)
            card.add_to_cart.connect(self.add_to_cart.emit)
            self._grid.addWidget(card, i // COLS, i % COLS)
