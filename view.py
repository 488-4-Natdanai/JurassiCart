"""
VIEW DINO
"""
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QColor
import sys


class ViewDino(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setGeometry(250, 100, 1260, 650)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.build_menu()
        self.build_header()
        self.build_body()

    # ─── MENU BAR ────────────────────────────────────────────────
    def build_menu(self):
        self.menuBar().addMenu("Edit")
        self.menuBar().addMenu("Navigation")
        self.menuBar().addMenu("Store")
        self.menuBar().addMenu("Account")

    # ─── HEADER ──────────────────────────────────────────────────
    def build_header(self):
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #1a6e1a;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        # Logo
        self.logo_btn = QPushButton("🦕  JurassiCart")
        self.logo_btn.setStyleSheet("""
            QPushButton {
                color: white; font-size: 20px; font-weight: bold;
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

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent;")

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        # Icon buttons
        icon_style = """
            QPushButton {
                color: white; font-size: 22px;
                background: transparent; border: none; padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
                border-radius: 20px;
            }
        """
        self.filter_btn  = QPushButton("⧩")
        self.cart_btn    = QPushButton("🛒")
        self.profile_btn = QPushButton("👤")

        for btn in [self.filter_btn, self.cart_btn, self.profile_btn]:
            btn.setFixedSize(44, 44)
            btn.setStyleSheet(icon_style)

        self.filter_btn.clicked.connect(lambda: print("Filter"))
        self.cart_btn.clicked.connect(lambda: print("Cart"))
        self.profile_btn.clicked.connect(lambda: print("Profile"))

        layout.addWidget(self.logo_btn)
        layout.addWidget(search_container, stretch=1)
        layout.addWidget(self.filter_btn)
        layout.addWidget(self.cart_btn)
        layout.addWidget(self.profile_btn)

        self.main_layout.addWidget(header)

    # ─── BODY ────────────────────────────────────────────────────
    def build_body(self):
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(30, 30, 30, 30)
        body_layout.setSpacing(30)

        # Left: image placeholder
        self.image_frame = QFrame()
        self.image_frame.setFixedSize(580, 380)
        self.image_frame.setStyleSheet("""
            QFrame {
                background-color: #d9d9d9;
                border-radius: 12px;
            }
        """)
        img_layout = QVBoxLayout(self.image_frame)
        img_layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel("🦕")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("font-size: 80px; background: transparent;")
        img_layout.addWidget(self.image_label)

        # Right: info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(10)
        info_layout.setAlignment(Qt.AlignTop)

        # Name
        self.name_label = QLabel("Tyrannosaurus Rex")
        self.name_label.setFont(QFont("Arial", 26, QFont.Bold))
        self.name_label.setStyleSheet("color: #111;")

        # Type
        self.type_label = QLabel("Carnivore")
        self.type_label.setFont(QFont("Arial", 13))
        self.type_label.setStyleSheet("color: #555;")

        # Price
        self.price_label = QLabel("~$25,000,000")
        self.price_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.price_label.setStyleSheet("color: #1a6e1a; margin-top: 10px;")

        # Variants label
        variants_label = QLabel("Variants")
        variants_label.setFont(QFont("Arial", 12))
        variants_label.setStyleSheet("color: #333; margin-top: 10px;")

        # Color variant buttons
        variants_widget = QWidget()
        variants_layout = QHBoxLayout(variants_widget)
        variants_layout.setContentsMargins(0, 0, 0, 0)
        variants_layout.setSpacing(10)
        variants_layout.setAlignment(Qt.AlignLeft)

        self.selected_variant = None
        variants = [("#1a6e1a", "Green"), ("#6b2f0e", "Brown"), ("#111111", "Black")]

        self.variant_buttons = []
        for color, name in variants:
            btn = QPushButton()
            btn.setFixedSize(46, 46)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 23px;
                    border: 3px solid transparent;
                }}
                QPushButton:hover {{
                    border: 3px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color, b=btn: self.select_variant(c, b))
            variants_layout.addWidget(btn)
            self.variant_buttons.append(btn)

        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignLeft)

        self.order_btn = QPushButton("Order")
        self.order_btn.setFixedSize(160, 50)
        self.order_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a6e1a; color: white;
                font-size: 16px; font-weight: bold;
                border-radius: 25px; border: none;
            }
            QPushButton:hover { background-color: #145214; }
        """)

        self.cart_add_btn = QPushButton("Add to cart")
        self.cart_add_btn.setFixedSize(180, 50)
        self.cart_add_btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: #111;
                font-size: 16px; font-weight: bold;
                border-radius: 25px;
                border: 2px solid #ccc;
            }
            QPushButton:hover { background-color: #f0f0f0; }
        """)

        self.order_btn.clicked.connect(lambda: print("Order clicked"))
        self.cart_add_btn.clicked.connect(lambda: print("Add to cart clicked"))

        buttons_layout.addWidget(self.order_btn)
        buttons_layout.addWidget(self.cart_add_btn)

        # Assemble right panel
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.type_label)
        info_layout.addWidget(self.price_label)
        info_layout.addWidget(variants_label)
        info_layout.addWidget(variants_widget)
        info_layout.addWidget(buttons_widget)
        info_layout.addStretch()

        body_layout.addWidget(self.image_frame)
        body_layout.addWidget(info_widget, stretch=1)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ccc;")

        self.main_layout.addWidget(body)
        self.main_layout.addWidget(line)
        self.main_layout.addStretch()

    def select_variant(self, color, clicked_btn):
        self.selected_variant = color
        for btn in self.variant_buttons:
            btn.setStyleSheet(btn.styleSheet().replace(
                "border: 3px solid white", "border: 3px solid transparent"
            ))
        clicked_btn.setStyleSheet(clicked_btn.styleSheet().replace(
            "border: 3px solid transparent", "border: 3px solid white"
        ))
        print(f"Variant selected: {color}")


def main():
    app = QApplication(sys.argv)
    window = ViewDino()
    window.show()
    sys.exit(app.exec())
    


if __name__ == "__main__":
    main()