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
        """Store the logged-in user and load their data into all relevant pages."""
        self.current_user = user
        self.account.load_user(user)
        self.cart.load_user(user)
        self.store.load_user(user)
        self.go(self.home)

    def _on_go_checkout(self, items: list, wallet: int):
        """Load checkout data and navigate to the checkout page."""
        self.checkout.load(items, wallet, self.current_user)
        self.go(self.checkout)

    def _on_add_to_cart(self, dino: dict):
        """Add a dino to the cart if the user is logged in, otherwise prompt login."""
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
        """Clear the current session and navigate to the home page."""
        self.current_user = None
        self.go(self.home)

    def _on_feedback(self):
        """Show feedback dialog and save message to database."""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                       QLabel, QTextEdit, QPushButton)
        dlg = QDialog(self)
        dlg.setWindowTitle("Give Feedback")
        dlg.setFixedSize(420, 260)
        dlg.setStyleSheet("background:white;")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("We'd love to hear your thoughts!")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("color:#111;")
        lay.addWidget(lbl)

        txt = QTextEdit()
        txt.setPlaceholderText("Write your feedback here...")
        txt.setFont(QFont("Segoe UI", 10))
        txt.setStyleSheet("border:1px solid #ccc;border-radius:8px;padding:8px;")
        lay.addWidget(txt, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(90, 34)
        cancel_btn.setStyleSheet("""
            QPushButton{background:#e0e0e0;border:none;border-radius:8px;color:#333;}
            QPushButton:hover{background:#ccc;}
        """)
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(90, 34)
        ok_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        ok_btn.setStyleSheet("""
            QPushButton{background:#0b7a12;border:none;border-radius:8px;color:white;}
            QPushButton:hover{background:#095e0e;}
        """)
        ok_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(ok_btn)
        lay.addLayout(btn_row)

        if dlg.exec() == QDialog.Accepted:
            msg = txt.toPlainText().strip()
            if msg:
                uid   = self.current_user["user_id"]  if self.current_user else "guest"
                uname = self.current_user["username"] if self.current_user else "guest"
                db.add_feedback(uid, uname, msg)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Thank you!", "Your feedback has been submitted.")

    def _show_filter_menu(self):
        """Show filter dropdown below the filter button."""
        btn = self.filter_btn
        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        self._filter_menu.exec(pos)

    def _on_filter_select(self, action):
        """Apply the selected gene filter and refresh the home page."""
        value = action.data()
        self._current_filter = value
        for act in self._filter_menu.actions():
            act.setChecked(act.data() == value)
        self.home.refresh(gene_filter=value, search=self.search_bar.text())

    def _on_search(self):
        """Read the search bar text and refresh the home page with the query."""
        query = self.search_bar.text().strip()
        # navigate to home if not already there
        if self.stack.currentWidget() != self.home:
            self.go(self.home)
        self.home.refresh(gene_filter=self._current_filter, search=query)

    def _on_profile_click(self):
        """Navigate to the account page if logged in, otherwise go to login."""
        if self.current_user:
            self.go(self.account)
        else:
            self.go(self.login)

    # ─────────────────────────────
    # Navigation system
    # ─────────────────────────────

    def go(self, page):
        """Navigate to a page, pushing the current page onto the back history."""
        current = self.stack.currentWidget()

        if current != page:
            self.history_back.append(current)
            self.history_forward.clear()

        self.stack.setCurrentWidget(page)


    def go_back(self):
        """Navigate to the previous page in the back history."""
        if not self.history_back:
            return

        current = self.stack.currentWidget()
        self.history_forward.append(current)

        page = self.history_back.pop()
        self.stack.setCurrentWidget(page)


    def go_forward(self):
        """Navigate to the next page in the forward history."""
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
        """Build the menu bar with Edit, Navigation, Store, and Account menus."""
        edit_menu = self.menuBar().addMenu("Edit")

        quit_btn = QAction("Quit", self)
        quit_btn.triggered.connect(sys.exit)
        edit_menu.addAction(quit_btn)

        feedback_btn = QAction("Give Feedback", self)
        feedback_btn.triggered.connect(self._on_feedback)
        edit_menu.addAction(feedback_btn)

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
        """Build the top toolbar with logo, search bar, filter, cart, and profile buttons."""
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

        search_icon.clicked.connect(self._on_search)
        self.search_bar.returnPressed.connect(self._on_search)

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
    """Entry point: initialise the Qt app, seed the database, and launch the main window."""
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