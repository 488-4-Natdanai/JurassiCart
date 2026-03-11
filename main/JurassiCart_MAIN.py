import sys, os
import ctypes

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolBar
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QAction, QFontDatabase, QIcon

from home import home
from reglog import login, register
from myprofile import profile, wallet, change_pass
from store import store, stock, addstock
from search import search
from view import view
from cart import cart, checkout


dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280,720)

        # navigation history
        self.history_back = []
        self.history_forward = []

        self.create_menu()
        self.create_toolbar()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.home = home()
        self.login = login()
        self.register = register()
        self.profile = profile()
        self.wallet = wallet()
        self.change_pass = change_pass()
        self.store = store()
        self.stock = stock()
        self.addstock = addstock()
        self.search = search()
        self.view = view()
        self.cart = cart()
        self.checkout = checkout()

        pages = [
            self.home, self.login, self.register, self.profile,
            self.wallet, self.change_pass, self.store,
            self.stock, self.addstock, self.search,
            self.view, self.cart, self.checkout
        ]

        for p in pages:
            self.stack.addWidget(p)

        self.stack.setCurrentWidget(self.home)
        self.login.switch_to_register.connect(lambda: self.go(self.register))
        self.register.switch_to_login.connect(lambda: self.go(self.login))


    # ─────────────────────────────
    # Navigation system
    # ─────────────────────────────

    def go(self, page):

        current = self.stack.currentWidget()

        if current != page:
            self.history_back.append(current)
            self.history_forward.clear()

        self.stack.setCurrentWidget(page)


    def go_back(self):

        if not self.history_back:
            return

        current = self.stack.currentWidget()
        self.history_forward.append(current)

        page = self.history_back.pop()
        self.stack.setCurrentWidget(page)


    def go_forward(self):

        if not self.history_forward:
            return

        current = self.stack.currentWidget()
        self.history_back.append(current)

        page = self.history_forward.pop()
        self.stack.setCurrentWidget(page)


    # ─────────────────────────────
    # MenuBar
    # ─────────────────────────────

    def create_menu(self):

        edit_menu = self.menuBar().addMenu("Edit")

        quit_btn = QAction("Quit", self)
        quit_btn.triggered.connect(sys.exit)
        edit_menu.addAction(quit_btn)

        nav_menu = self.menuBar().addMenu("Navigation")

        back_btn = QAction("Go Back", self)
        back_btn.triggered.connect(self.go_back)
        nav_menu.addAction(back_btn)

        forward_btn = QAction("Go Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        nav_menu.addAction(forward_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(lambda: self.go(self.home))
        nav_menu.addAction(home_btn)


        store_menu = self.menuBar().addMenu("Store")

        create_store = QAction("Create store", self)
        create_store.triggered.connect(lambda: self.go(self.store))
        store_menu.addAction(create_store)

        stock_btn = QAction("Stock", self)
        stock_btn.triggered.connect(lambda: self.go(self.stock))
        store_menu.addAction(stock_btn)

        add_stock = QAction("Add stock", self)
        add_stock.triggered.connect(lambda: self.go(self.addstock))
        store_menu.addAction(add_stock)


        acc_menu = self.menuBar().addMenu("Account")

        myacc = QAction("My profile", self)
        myacc.triggered.connect(lambda: self.go(self.login))
        acc_menu.addAction(myacc)

        cart_btn = QAction("My Cart", self)
        cart_btn.triggered.connect(lambda: self.go(self.cart))
        acc_menu.addAction(cart_btn)


    # ─────────────────────────────
    # Toolbar
    # ─────────────────────────────

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
        layout.setContentsMargins(20,8,20,8)
        layout.setSpacing(15)

        icon_style = """
        QPushButton{
            background:transparent;
            border:none;
        }
        QPushButton:hover{
            background-color:rgba(255,255,255,0.2);
            border-radius:20px;
        }
        """

        def icon_btn(path,size=40):
            btn = QPushButton()
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(size,size))
            btn.setFixedSize(44,44)
            btn.setStyleSheet(icon_style)
            return btn


        # Logo
        self.logo = icon_btn(juras_logo)

        self.name_btn = QPushButton("JurassiCart")

        font_path = os.path.join(dir,"resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.name_btn.setFont(QFont(font_family,12))

        self.name_btn.setStyleSheet("""
        QPushButton{
            color:white;
            font-size:30px;
            font-weight:bold;
            background:transparent;
            border:none;
        }
        QPushButton:hover{color:#ccffcc;}
        """)


        # Search
        search_container = QWidget()
        search_container.setStyleSheet("""
        QWidget{
            background:white;
            border-radius:20px;
        }
        """)

        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15,0,10,0)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setFixedHeight(40)

        self.search_bar.setStyleSheet("""
        QLineEdit{
            border:none;
            background:transparent;
            font-size:14px;
        }
        """)

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(dir,"resorces","search.png")))
        search_icon.setIconSize(QSize(24,24))
        search_icon.setFixedSize(44,44)

        search_icon.setStyleSheet("""
        QPushButton{
            background:transparent;
            border:none;
        }
        QPushButton:hover{
            background:#999999;
            border-radius:22px;
        }
        """)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_icon)


        # Right icons
        self.filter_btn = icon_btn(os.path.join(dir,"resorces","filter.png"),24)
        self.cart_btn = icon_btn(os.path.join(dir,"resorces","cart.png"))
        self.profile_btn = icon_btn(os.path.join(dir,"resorces","user.png"))


        # Navigation connections
        self.logo.clicked.connect(lambda: self.go(self.home))
        self.name_btn.clicked.connect(lambda: self.go(self.home))

        search_icon.clicked.connect(lambda: self.go(self.search))

        self.cart_btn.clicked.connect(lambda: self.go(self.cart))
        self.profile_btn.clicked.connect(lambda: self.go(self.login))


        layout.addWidget(self.logo)
        layout.addWidget(self.name_btn)
        layout.addWidget(search_container,stretch=1)
        layout.addWidget(self.filter_btn)
        layout.addWidget(self.cart_btn)
        layout.addWidget(self.profile_btn)

        toolbar.addWidget(container)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

def main():

    myappid = "dme.jurassicart.app"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    sys.argv += ['-platform','windows:darkmode=1']

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(dino_logo))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()