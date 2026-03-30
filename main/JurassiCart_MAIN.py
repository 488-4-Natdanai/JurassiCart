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
from account import AccountPage
from store import StorePage
from view import view
from cart import CartPage, CheckoutPage
import database as db


dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280,720)

        # ── session ──────────────────────────────
        self.current_user: dict | None = None   # set after login

        # navigation history
        self.history_back = []
        self.history_forward = []

        self.create_menu()
        self.create_toolbar()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.home     = home()
        self.login    = login()
        self.register = register()
        self.account  = AccountPage()
        self.store    = StorePage()
        self.view     = view()
        self.cart     = CartPage()
        self.checkout = CheckoutPage()

        pages = [
            self.home, self.login, self.register, self.account,
            self.store, self.view, self.cart, self.checkout
        ]

        for p in pages:
            self.stack.addWidget(p)

        self.stack.setCurrentWidget(self.home)

        # ── signal wiring ─────────────────────────
        self.login.switch_to_register.connect(lambda: self.go(self.register))
        self.register.switch_to_login.connect(lambda: self.go(self.login))

        self.login.login_success.connect(self._on_login_success)
        # register_success ถูกเอาออกแล้ว — register จะกลับไป login page แทน

        # cart → checkout
        self.cart.go_checkout.connect(self._on_go_checkout)

        # home → cart (add to cart from home page)
        self.home.add_to_cart.connect(self._on_add_to_cart)

        # store add stock → home refresh
        self.store.item_added.connect(self.home.refresh)

    # ─────────────────────────────
    # Session helpers
    # ─────────────────────────────

    def _on_login_success(self, user: dict):
        self.current_user = user
        self.account.load_user(user)
        self.cart.load_user(user)
        self.store.load_user(user)
        self.go(self.home)

    def _on_go_checkout(self, items: list, wallet: int):
        self.checkout.load(items, wallet, self.current_user)
        self.go(self.checkout)

    def _on_add_to_cart(self, dino: dict):
        if not self._require_login():
            return
        self.cart.add_item(dino)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Added to Cart", f"{dino['name']} added to cart!")

    def _require_login(self) -> bool:
        """Return True if logged in, else show prompt and go to login."""
        if self.current_user:
            return True
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Login Required",
            "You need to log in to use this feature.\nGo to login page?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.go(self.login)
        return False


    def _on_logout(self):
        self.current_user = None
        self.go(self.home)

    def _show_filter_menu(self):
        """Show filter dropdown below the filter button."""
        btn = self.filter_btn
        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        self._filter_menu.exec(pos)

    def _on_filter_select(self, action):
        value = action.data()
        self._current_filter = value
        # update checkmarks
        for act in self._filter_menu.actions():
            act.setChecked(act.data() == value)
        # apply filter — only affects home page
        self.home.refresh(gene_filter=value)

    def _on_profile_click(self):
        if self.current_user:
            self.go(self.account)
        else:
            self.go(self.login)

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
        create_store.triggered.connect(lambda: self.go(self.store) if self._require_login() else None)
        store_menu.addAction(create_store)

        stock_btn = QAction("Stock", self)
        stock_btn.triggered.connect(lambda: self.go(self.store) if self._require_login() else None)
        store_menu.addAction(stock_btn)

        add_stock = QAction("Add stock", self)
        add_stock.triggered.connect(lambda: self.go(self.store) if self._require_login() else None)
        store_menu.addAction(add_stock)


        acc_menu = self.menuBar().addMenu("Account")

        myacc = QAction("My profile", self)
        myacc.triggered.connect(lambda: self.go(self.account) if self._require_login() else None)
        acc_menu.addAction(myacc)

        cart_btn = QAction("My Cart", self)
        cart_btn.triggered.connect(lambda: self.go(self.cart) if self._require_login() else None)
        acc_menu.addAction(cart_btn)

        logout_btn = QAction("Logout", self)
        logout_btn.triggered.connect(self._on_logout)
        acc_menu.addAction(logout_btn)


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

        search_icon.clicked.connect(lambda: self.go(self.search) if hasattr(self, 'search') else None)

        self.cart_btn.clicked.connect(lambda: self.go(self.cart) if self._require_login() else None)
        self.profile_btn.clicked.connect(self._on_profile_click)

        # filter dropdown
        from PySide6.QtWidgets import QMenu
        self._filter_menu = QMenu(self)
        self._filter_menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 8px 24px;
                font-size: 11pt;
                color: #222;
            }
            QMenu::item:selected { background: #e8f5e9; color: #0b7a12; }
            QMenu::item:checked  { font-weight: bold; color: #0b7a12; }
        """)
        self._filter_menu.setToolTipsVisible(False)
        self._current_filter = ""

        for label, value in [("All (Default)", ""), ("Carnivore", "Carnivore"),
                              ("Herbivore", "Herbivore"), ("Omnivore", "Omnivore")]:
            act = self._filter_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(value == self._current_filter)
            act.setData(value)

        self._filter_menu.triggered.connect(self._on_filter_select)
        self.filter_btn.clicked.connect(self._show_filter_menu)


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

    db.seed_dinosaurs()   # seed sample data on first run

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()