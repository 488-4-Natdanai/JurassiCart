import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon
from view import ViewDino
dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")

class account(QWidget):
    def __init__(self):
        super().__init__()

    def _build_ui(self):
        pass #สร้าง UI ตรงนี้เลยนะ 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()
        
    def create_menu(self):

        #Edit menu
        edit_menu = self.menuBar().addMenu("Edit")

        gen = QAction("Quit", self)
        gen.triggered.connect(sys.exit)
        edit_menu.addAction(gen)

        #Navigation menu
        nav_menu = self.menuBar().addMenu("Navigation")

        go_back = QAction("Go back", self)
        go_back.triggered.connect(lambda : print("go back"))
        nav_menu.addAction(go_back)

        go_forward = QAction("Go forward", self)
        go_forward.triggered.connect(lambda : print("go forward"))
        nav_menu.addAction(go_forward)

        go_home = QAction("Home", self)
        go_home.triggered.connect(lambda : print("go home"))
        nav_menu.addAction(go_home)

        #Store menu
        store_menu = self.menuBar().addMenu("Store")

        create_store = QAction("Create store", self)
        create_store.triggered.connect(lambda : print("create store"))
        store_menu.addAction(create_store)

        stock = QAction("Stock", self)
        stock.triggered.connect(lambda : print("go stock"))
        store_menu.addAction(stock)

        add_stock = QAction("Add stock", self)
        add_stock.triggered.connect(lambda : print("go add_stock"))
        store_menu.addAction(add_stock)

        #Acc menu
        acc_menu = self.menuBar().addMenu("Account")

        myacc = QAction("My account", self)
        myacc.triggered.connect(lambda : print("create store"))
        acc_menu.addAction(myacc)

        cart = QAction("My Cart", self)
        cart.triggered.connect(lambda : print("go cart"))
        acc_menu.addAction(cart)
        
    def create_toolbar(self):
        toolbar = QToolBar("TopBar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar{
            background:#0b7a12;
            spacing:10px;
            padding:8px;
        }
        """)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        # Icon buttons
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
        # Logo
        self.logo = QPushButton()
        self.logo.setIcon(QIcon(juras_logo))
        self.logo.setIconSize(QSize(40,40))

        self.name_btn = QPushButton("JurassiCart")
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.name_btn.setFont(QFont(font_family, 12))
        self.name_btn.setStyleSheet("""
            QPushButton {
                color: white; font-size: 30px; font-weight: bold;
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

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(dir, "resorces","search.png")))
        search_icon.clicked.connect(lambda : print("Search"))
        search_icon.setStyleSheet("background: #999999;")
        search_icon.setFixedSize(44, 44)
        search_icon.setIconSize(QSize(24,24))
        search_icon.setStyleSheet("""
            QPushButton {
                color: white; font-size: 40px;
                background: transparent; border: none; padding: 5px;
            }
            QPushButton:hover {
                background-color: #999999;
                border-radius: 22px;
            }
        """)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)

        self.filter_btn  = QPushButton()
        self.filter_btn.setIcon(QIcon(os.path.join(dir, "resorces","filter.png")))
        self.filter_btn.setIconSize(QSize(24,24))
        self.cart_btn    = QPushButton()
        self.cart_btn.setIcon(QIcon(os.path.join(dir, "resorces","cart.png")))
        self.cart_btn.setIconSize(QSize(40,40))
        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(os.path.join(dir, "resorces","user.png")))
        self.profile_btn.setIconSize(QSize(40,40))

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