import sys, os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,QLabel, QLineEdit, QDateEdit,
    QSpinBox,QPushButton, QDialog, QMessageBox, QScrollArea,QFrame, QSizePolicy, QToolBar)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QAction, QPixmap, QFontDatabase, QIcon
dir = os.path.dirname(os.path.abspath(__file__))
dino_logo = os.path.join(dir, "resorces","dino2.png")
juras_logo = os.path.join(dir, "resorces","JurassiLogo.png")

class login(QWidget):
    switch_to_register = Signal()
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ------------------
        # LEFT SIDE (IMAGE)
        # ------------------
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pix = QPixmap(os.path.join(dir,"resorces","longneck.jpg"))  # เปลี่ยนรูปตรงนี้
        self.left.setPixmap(self.pix)
        

        # ------------------
        # RIGHT SIDE
        # ------------------
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")

        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        # Login Card
        card = QFrame()
        card.setFixedSize(450, 500)
        card.setStyleSheet("""
        QFrame{
            background:white;
            border-radius:10px;
        }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0,0,0,20)

        # Header
        header = QLabel("  Login")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        header.setFont(QFont(font_family, 12))
        header.setFixedHeight(60)
        header.setStyleSheet("""
        QLabel{
            background:#0b7a12;
            color:white;
            font-size:28px;
            border-top-left-radius:10px;
            border-top-right-radius:10px;
        }
        """)

        # Inputs
        form = QVBoxLayout()
        form.setContentsMargins(30,20,30,10)
        form.setSpacing(15)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        for box in [self.username, self.password]:
            box.setFixedHeight(45)
            box.setStyleSheet("""
            QLineEdit{
                border:1px solid #ccc;
                border-radius:15px;
                padding-left:10px;
                background:#f3f3f3;
            }
            """)

        login_btn = QPushButton("LOGIN")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
        QPushButton{
            background:#0b7a12;
            color:white;
            font-weight:bold;
            border-radius:8px;
        }
        QPushButton:hover{
            background:#0d9416;
        }
        """)

        signup = QLabel("Don't have an account? <a href='#'>REGISTER</a>")
        signup.setAlignment(Qt.AlignCenter)
        signup.setTextInteractionFlags(Qt.TextBrowserInteraction)
        signup.setOpenExternalLinks(False)
        signup.linkActivated.connect(lambda: self.switch_to_register.emit())

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(login_btn)
        form.addWidget(signup)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)

        right_layout.addWidget(card)

        main_layout.addWidget(self.left,3)
        main_layout.addWidget(right_container,2)

class register(QWidget):
    switch_to_login = Signal()
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self._build_ui()

    def _build_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ------------------
        # LEFT SIDE (IMAGE)
        # ------------------
        self.left = QLabel()
        self.left.setScaledContents(True)
        self.left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pix = QPixmap(os.path.join(dir,"resorces","reg.jpg"))  # เปลี่ยนรูปตรงนี้
        self.left.setPixmap(self.pix)
        

        # ------------------
        # RIGHT SIDE
        # ------------------
        right_container = QWidget()
        right_container.setStyleSheet("background:#eeeeee;")

        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignCenter)

        # Login Card
        card = QFrame()
        card.setFixedSize(450, 500)
        card.setStyleSheet("""
        QFrame{
            background:white;
            border-radius:10px;
        }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0,0,0,20)

        # Header
        header = QLabel("  Register")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_path = os.path.join(dir, "resorces","DinopiaRegular-mLrO9.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        header.setFont(QFont(font_family, 12))
        header.setFixedHeight(60)
        header.setStyleSheet("""
        QLabel{
            background:#0b7a12;
            color:white;
            font-size:28px;
            border-top-left-radius:10px;
            border-top-right-radius:10px;
        }
        """)

        # Inputs
        form = QVBoxLayout()
        form.setContentsMargins(30,20,30,10)
        form.setSpacing(15)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm password")
        self.confirm.setEchoMode(QLineEdit.Password)

        for box in [self.username, self.password, self.confirm]:
            box.setFixedHeight(45)
            box.setStyleSheet("""
            QLineEdit{
                border:1px solid #ccc;
                border-radius:15px;
                padding-left:10px;
                background:#f3f3f3;
            }
            """)

        register_btn = QPushButton("REGISTER")
        register_btn.setFixedHeight(45)
        register_btn.setStyleSheet("""
        QPushButton{
            background:#0b7a12;
            color:white;
            font-weight:bold;
            border-radius:8px;
        }
        QPushButton:hover{
            background:#0d9416;
        }
        """)

        login = QLabel("Already have an account? <a href='#'>LOGIN</a>")
        login.setAlignment(Qt.AlignCenter)
        login.setTextInteractionFlags(Qt.TextBrowserInteraction)
        login.setOpenExternalLinks(False)
        login.linkActivated.connect(lambda: self.switch_to_login.emit())

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.confirm)
        form.addWidget(register_btn)
        form.addWidget(login)
        form.addStretch()

        card_layout.addWidget(header)
        card_layout.addLayout(form)

        right_layout.addWidget(card)

        main_layout.addWidget(self.left,3)
        main_layout.addWidget(right_container,2)
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JurassiCart")
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.create_menu()
        self.create_toolbar()
        self.setCentralWidget(register())
        self.stack = QStackedWidget()

        self.login_page = login()
        self.register_page = register()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)

        self.setCentralWidget(self.stack)
        self.login_page.switch_to_register.connect(
        lambda: self.stack.setCurrentWidget(self.register_page))

        self.register_page.switch_to_login.connect(
        lambda: self.stack.setCurrentWidget(self.login_page))
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