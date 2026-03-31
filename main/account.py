from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QStackedWidget,
    QDateEdit, QDialog, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate, QPoint, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPolygon, QPen, QIcon
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database as db

_DIR = os.path.dirname(os.path.abspath(__file__))
DINO_LOGO_PATH  = os.path.join(_DIR, "resorces", "dino2.png")
USER_AVATAR_PATH = os.path.join(_DIR, "resorces", "user.png")

# ─────────────────────────────────────────────
# Helper: create simple icon with QPainter
# (Used for icons without provided images like 'back' and 'cart')
# ─────────────────────────────────────────────
def create_simple_icon(type, size=32, color="#ffffff"):
    """Draw and return a simple QPainter-based icon for 'back' or 'cart' types."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(color), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)

    if type == "back":
        p.drawPolyline([QPoint(size * 0.7, size * 0.3),
                        QPoint(size * 0.3, size * 0.5),
                        QPoint(size * 0.7, size * 0.7)])
    elif type == "cart":
        p.drawRect(int(size * 0.2), int(size * 0.35), int(size * 0.6), int(size * 0.5))
        p.drawEllipse(int(size * 0.25), int(size * 0.85), 4, 4)
        p.drawEllipse(int(size * 0.65), int(size * 0.85), 4, 4)
        p.drawPolyline([QPoint(size * 0.2, size * 0.35),
                        QPoint(size * 0.1, size * 0.15),
                        QPoint(size * 0.3, size * 0.15)])

    p.end()
    return QIcon(px)


# ─────────────────────────────────────────────
# Style constants
# ─────────────────────────────────────────────
OVAL_BTN_GREEN = """
    QPushButton {{
        background: #2e7d32; color: white;
        border: none; border-radius: {r}px;
    }}
    QPushButton:hover   {{ background: #1b5e20; }}
    QPushButton:pressed {{ background: #388e3c; }}
"""

OVAL_BTN_OUTLINE = """
    QPushButton {{
        background: white; color: #333;
        border: 1px solid #aaa; border-radius: {r}px;
    }}
    QPushButton:hover {{ background: #f5f5f5; border-color: #888; }}
"""

OVAL_BTN_RED = """
    QPushButton {{
        background: #e53935; color: white;
        border: none; border-radius: {r}px;
    }}
    QPushButton:hover {{ background: #c62828; }}
"""

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }
    QLineEdit:focus { border: 1.5px solid #2e7d32; }
"""

def combo_style():
    """Return the stylesheet string for a rounded QComboBox."""
    return f"""
    QComboBox {{
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }}
    QComboBox:focus {{ border: 1.5px solid #2e7d32; }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px; border: none; background: transparent;
    }}
    QComboBox::down-arrow {{
        width: 12px; height: 8px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid #ccc;
        selection-background-color: #c8e6c9;
    }}
"""

def date_style():
    """Return the stylesheet string for a rounded QDateEdit."""
    return f"""
    QDateEdit {{
        border: 1px solid #ccc; border-radius: 17px;
        padding: 0 14px; background: white; color: #222;
    }}
    QDateEdit:focus {{ border: 1.5px solid #2e7d32; }}
    QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px; border: none; background: transparent;
    }}
    QDateEdit::down-arrow {{
        width: 12px; height: 8px;
    }}
"""

# ─────────────────────────────────────────────
# Tab Bar
# ─────────────────────────────────────────────
class TabBar(QWidget):
    tab_changed = Signal(int)

    def __init__(self, tabs, parent=None):
        super().__init__(parent)
        self.active = 0
        self._buttons = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, name in enumerate(tabs):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(46)
            btn.setMinimumWidth(160)
            btn.clicked.connect(lambda _, idx=i: self._on_click(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        self._update_styles()

    def _on_click(self, idx):
        """Handle tab button click, update active index, and emit tab_changed."""
        self.active = idx
        self._update_styles()
        self.tab_changed.emit(idx)

    def _update_styles(self):
        """Apply active/inactive styles to all tab buttons."""
        for i, btn in enumerate(self._buttons):
            if i == self.active:
                btn.setStyleSheet("""
                    QPushButton {
                        background: white; border: none;
                        color: #222; font-weight: 600; padding: 0 24px;
                    }
                """)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #e8e8e8; border: none;
                        color: #555; font-weight: 400; padding: 0 24px;
                    }
                    QPushButton:hover { background: #f0f0f0; color: #222; }
                """)
                btn.setChecked(False)


# ─────────────────────────────────────────────
# Page 0 — My Profile
# ─────────────────────────────────────────────
class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_id = None
        self.setStyleSheet("background: white;")

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)
        label_width = 110

        # Username (read-only)
        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Username"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        self.username_lbl = QLabel("")
        self.username_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.username_lbl.setStyleSheet("color:#333;")
        row.addWidget(self.username_lbl); row.addStretch()
        form_layout.addLayout(row)

        self.fields = {}
        for label_text, placeholder, key in [
            ("Name",         "Enter your name",         "name"),
            ("Email",        "Enter your email",        "email"),
            ("Phone Number", "Enter your phone number", "phone"),
        ]:
            row = QHBoxLayout(); row.setSpacing(12)
            lbl = QLabel(label_text); lbl.setFixedWidth(label_width)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
            row.addWidget(lbl)
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setFont(QFont("Segoe UI", 10))
            field.setFixedHeight(34); field.setMinimumWidth(260)
            field.setStyleSheet(INPUT_STYLE)
            self.fields[key] = field
            row.addWidget(field); row.addStretch()
            form_layout.addLayout(row)

        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Gender"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        gender_cb = QComboBox()
        gender_cb.addItems(["Female", "Male", "Other"])
        gender_cb.setFont(QFont("Segoe UI", 10))
        gender_cb.setFixedHeight(34); gender_cb.setMinimumWidth(160)
        gender_cb.setStyleSheet(combo_style())
        row.addWidget(gender_cb); row.addStretch()
        form_layout.addLayout(row)

        # Date of birth
        row = QHBoxLayout(); row.setSpacing(12)
        lbl = QLabel("Date of birth"); lbl.setFixedWidth(label_width)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
        row.addWidget(lbl)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(2001, 1, 1))
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setFont(QFont("Segoe UI", 10))
        date_edit.setFixedHeight(34); date_edit.setMinimumWidth(160)
        date_edit.setStyleSheet(date_style())
        row.addWidget(date_edit); row.addStretch()
        form_layout.addLayout(row)

        form_layout.addSpacing(10)

        # Save button
        save_row = QHBoxLayout()
        save_row.addSpacing(label_width + 12)
        save_btn = QPushButton("Save")
        save_btn.setFixedSize(100, 38)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
        save_btn.clicked.connect(self._on_save)
        save_row.addWidget(save_btn); save_row.addStretch()
        form_layout.addLayout(save_row)
        form_layout.addStretch()

        root.addLayout(form_layout, stretch=3)

        # Avatar
        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        avatar_layout.setSpacing(14)

        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(120, 120)
        self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("background:#ddd; border-radius:60px;")
        self._set_avatar_pixmap(USER_AVATAR_PATH)

        avatar_layout.addWidget(self.avatar_lbl)
        select_btn = QPushButton("Select Image")
        select_btn.setFixedSize(120, 34)
        select_btn.setFont(QFont("Segoe UI", 9))
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.setStyleSheet(OVAL_BTN_OUTLINE.format(r=17))
        select_btn.clicked.connect(self._on_select_avatar)
        avatar_layout.addWidget(select_btn, alignment=Qt.AlignHCenter)
        avatar_layout.addStretch()

        root.addLayout(avatar_layout, stretch=1)

    def load_user(self, user: dict):
        """Populate profile fields from the given user dict."""
        self._user_id = user["user_id"]
        self.username_lbl.setText(user.get("username", ""))
        self.fields["name"].setText(user.get("name", ""))
        self.fields["email"].setText(user.get("email", ""))
        self.fields["phone"].setText(user.get("phone", ""))
        avatar = user.get("avatar", "")
        self._set_avatar_pixmap(avatar if avatar and os.path.exists(avatar) else USER_AVATAR_PATH)

    def _set_avatar_pixmap(self, path: str):
        """Load and display avatar image, fallback to grey circle."""
        px = QPixmap(path).scaled(120, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) if path else QPixmap()
        if px.isNull():
            px = QPixmap(120, 120); px.fill(QColor("#ddd"))
        self.avatar_lbl.setPixmap(px)

    def _on_select_avatar(self):
        """Open file dialog, copy selected image to resorces/avatars/, save to DB."""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Avatar", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if not path:
            return
        import shutil
        avatar_dir = os.path.join(_DIR, "resorces", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        ext = os.path.splitext(path)[-1]
        dest = os.path.join(avatar_dir, f"{self._user_id}{ext}")
        shutil.copy2(path, dest)
        self._set_avatar_pixmap(dest)
        if self._user_id:
            db.update_user(self._user_id, avatar=dest)

    def _on_save(self):
        """Save updated profile fields to the database and show a confirmation dialog."""
        if not self._user_id:
            return
        db.update_user(
            self._user_id,
            name=self.fields["name"].text().strip(),
            email=self.fields["email"].text().strip(),
            phone=self.fields["phone"].text().strip(),
        )
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Saved", "Profile updated successfully.")

# ─────────────────────────────────────────────
# Popup — Purchase Info
# ─────────────────────────────────────────────
class PurchaseDialog(QDialog):
    def __init__(self, amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Purchase info")
        self.resize(420, 320)
        self.setStyleSheet("background: #f7f7f7;")
        self.setWindowIcon(QIcon(DINO_LOGO_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("PAYMENT")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #222;")
        layout.addWidget(title)

        # Method Label
        lbl_method = QLabel("Please select a payment method")
        lbl_method.setFont(QFont("Segoe UI", 9))
        lbl_method.setStyleSheet("color: #333;")
        layout.addWidget(lbl_method)

        # Combo Box
        self.combo = QComboBox()
        self.combo.addItems(["Promptpay", "Credit / Debit Card", "Bank Transfer"])
        self.combo.setFixedHeight(36)
        self.combo.setFont(QFont("Segoe UI", 10))
        self.combo.setStyleSheet(combo_style())
        layout.addWidget(self.combo)

        layout.addSpacing(10)

        # Line 1
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("color: #ccc;")
        layout.addWidget(line1)

        # Total
        total_layout = QHBoxLayout()
        lbl_total = QLabel("Total:")
        lbl_total.setFont(QFont("Segoe UI", 12))
        lbl_total.setStyleSheet("color: #222;")
        
        val_total = QLabel(f"${amount:,}")
        val_total.setFont(QFont("Segoe UI", 12))
        val_total.setStyleSheet("color: #222;")
        val_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        total_layout.addWidget(lbl_total)
        total_layout.addWidget(val_total)
        layout.addLayout(total_layout)

        # Line 2
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color: #ccc;")
        layout.addWidget(line2)

        layout.addSpacing(5)

        # Checkbox & Terms
        agree_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        # generate checkmark icon programmatically
        from PySide6.QtGui import QPainter, QPen
        chk_px = QPixmap(20, 20)
        chk_px.fill(Qt.transparent)
        p = QPainter(chk_px)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("white"), 2.5))
        p.drawLine(3, 10, 8, 15)
        p.drawLine(8, 15, 17, 5)
        p.end()
        chk_icon_path = os.path.join(_DIR, "resorces", "_check.png")
        chk_px.save(chk_icon_path)

        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid #555;
                background: white;
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid #2e7d32;
                background: #2e7d32;
                image: url({chk_icon_path.replace(os.sep, '/')});
            }}
        """)
        self.checkbox.setCursor(Qt.PointingHandCursor)
        
        lbl_terms = QLabel('I agree to the terms of the <a href="https://youtu.be/dQw4w9WgXcQ?si=gR7vhtV4-cmOPb_U" style="color:#1565c0;"><u>JurassiCart purchase agreement</u></a>')
        lbl_terms.setFont(QFont("Segoe UI", 9))
        lbl_terms.setStyleSheet("color: #222;")
        lbl_terms.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl_terms.setOpenExternalLinks(True)
        
        agree_layout.addWidget(self.checkbox)
        agree_layout.addWidget(lbl_terms)
        agree_layout.addStretch()
        layout.addLayout(agree_layout)

        layout.addSpacing(15)

        # Purchase Button
        btn_layout = QHBoxLayout()
        self.btn_purchase = QPushButton("Purchase")
        self.btn_purchase.setFixedSize(120, 38)
        self.btn_purchase.setFont(QFont("Segoe UI", 11))
        self.btn_purchase.setCursor(Qt.PointingHandCursor)
        
        self.btn_purchase.setEnabled(False) 
        self.btn_purchase.setStyleSheet("""
            QPushButton {
                background: white; color: #222;
                border: 1px solid #ddd; border-radius: 19px;
            }
            QPushButton:hover:enabled { background: #f0f0f0; border-color: #bbb; }
            QPushButton:disabled { color: #aaa; background: #e0e0e0; border: none; }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_purchase)
        layout.addLayout(btn_layout)
        layout.addStretch()

        # Connect Events
        self.checkbox.toggled.connect(self.btn_purchase.setEnabled)
        self.btn_purchase.clicked.connect(self.accept)

    def _on_check(self, state):
        """Enable or disable the purchase button based on checkbox state."""
        self.btn_purchase.setEnabled(state == Qt.Checked)

# ─────────────────────────────────────────────
# Page 1 — Wallet
# ─────────────────────────────────────────────
class WalletPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white;")
        self._user_id = None
        self.current_balance = 0

        root = QHBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(40)

        left = QVBoxLayout()
        left.setSpacing(10)

        for amount in [5_000_000, 10_000_000, 50_000_000,
                       100_000_000, 500_000_000, 1_000_000_000]:
            row = QHBoxLayout()
            row.setSpacing(16)

            label_frame = QFrame()
            label_frame.setStyleSheet("QFrame { background: #e8e8e8; border-radius: 21px; }")
            label_frame.setFixedHeight(42)
            label_frame.setMinimumWidth(260)
            
            label_inner = QHBoxLayout(label_frame)
            label_inner.setContentsMargins(20, 0, 20, 0)
            lbl = QLabel(f"Add ${amount:,}")
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #222; background: transparent;")
            label_inner.addWidget(lbl)
            row.addWidget(label_frame)

            add_btn = QPushButton("Add funds")
            add_btn.setFixedSize(110, 38)
            add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            add_btn.setCursor(Qt.PointingHandCursor)
            add_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
            
            add_btn.clicked.connect(lambda checked=False, amt=amount: self._open_purchase_dialog(amt))
            
            row.addWidget(add_btn)
            row.addStretch()
            left.addLayout(row)

        left.addStretch()
        root.addLayout(left, stretch=3)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)
        right.setSpacing(6)
        
        t = QLabel("Wallet Balance")
        t.setFont(QFont("Segoe UI", 11))
        t.setStyleSheet("color:#555;")
        right.addWidget(t)
        
        self.balance_lbl = QLabel(f"${self.current_balance:,}")
        self.balance_lbl.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.balance_lbl.setStyleSheet("color:#2e7d32;")
        right.addWidget(self.balance_lbl)
        
        right.addStretch()
        root.addLayout(right, stretch=2)

    def _open_purchase_dialog(self, amount):
        """Open the payment dialog and add funds to the wallet if confirmed."""
        dialog = PurchaseDialog(amount, self)
        if dialog.exec() == QDialog.Accepted:
            if self._user_id:
                self.current_balance = db.add_wallet(self._user_id, amount)
            else:
                self.current_balance += amount
            self.balance_lbl.setText(f"${self.current_balance:,}")

    def load_user(self, user: dict):
        """Load wallet balance and user ID from the given user dict."""
        self._user_id = user["user_id"]
        self.balance_lbl.setText(f"${self.current_balance:,}")

# ─────────────────────────────────────────────
# Page 2 — Change Password
# ─────────────────────────────────────────────
class ChangePasswordPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_id = None
        self.setStyleSheet("background: white;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(0)

        label_width = 150

        def make_field(label_text):
            row = QHBoxLayout(); row.setSpacing(12)
            lbl = QLabel(label_text); lbl.setFixedWidth(label_width)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFont(QFont("Segoe UI", 10)); lbl.setStyleSheet("color:#333;")
            row.addWidget(lbl)
            field = QLineEdit()
            field.setEchoMode(QLineEdit.Password)
            field.setFont(QFont("Segoe UI", 10))
            field.setFixedHeight(34); field.setMinimumWidth(280)
            field.setStyleSheet(INPUT_STYLE)
            row.addWidget(field); row.addStretch()
            return row, field

        row0, self.f_current = make_field("Current Password")
        layout.addLayout(row0)
        layout.addSpacing(20)

        row1, self.f_new = make_field("New Password")
        layout.addLayout(row1)
        layout.addSpacing(14)

        row2, self.f_confirm = make_field("Confirm Password")
        layout.addLayout(row2)
        layout.addSpacing(10)

        # Forget password row
        forget_row = QHBoxLayout()
        forget_row.addSpacing(label_width + 12)
        forget_lbl = QLabel('Forget password?  ')
        forget_lbl.setFont(QFont("Segoe UI", 9))
        forget_lbl.setStyleSheet("color:#555;")
        contact_lbl = QLabel('<a href="https://youtu.be/dQw4w9WgXcQ?si=gR7vhtV4-cmOPb_U" style="color:#1565c0;">contact us</a>')
        contact_lbl.setFont(QFont("Segoe UI", 9))
        contact_lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
        contact_lbl.setOpenExternalLinks(True)
        forget_row.addWidget(forget_lbl)
        forget_row.addWidget(contact_lbl)
        forget_row.addStretch()
        layout.addLayout(forget_row)
        layout.addSpacing(20)

        # error label
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignLeft)
        self.error_lbl.setStyleSheet("color:#cc0000; font-size:9pt;")
        self.error_lbl.setVisible(False)
        err_row = QHBoxLayout()
        err_row.addSpacing(label_width + 12)
        err_row.addWidget(self.error_lbl)
        err_row.addStretch()
        layout.addLayout(err_row)

        btn_row = QHBoxLayout()
        btn_row.addSpacing(label_width + 12)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setFixedSize(110, 38)
        confirm_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(OVAL_BTN_GREEN.format(r=19))
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn); btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

    def load_user(self, user: dict):
        """Store the user ID for use when changing the password."""
        self._user_id = user["user_id"]

    def _on_confirm(self):
        """Validate inputs, verify current password, and update to the new password."""
        from PySide6.QtWidgets import QMessageBox
        current  = self.f_current.text()
        new_pw   = self.f_new.text()
        confirm  = self.f_confirm.text()

        if not current or not new_pw or not confirm:
            self._show_error("All fields are required.")
            return
        if len(new_pw) < 6:
            self._show_error("New password must be at least 6 characters.")
            return
        if new_pw != confirm:
            self._show_error("New passwords do not match.")
            return

        # verify current password against DB
        user = db.get_user(self._user_id) if self._user_id else None
        if not user:
            self._show_error("Session error. Please log in again.")
            return

        import hashlib
        if user["password_hash"] != hashlib.sha256(current.encode()).hexdigest():
            self._show_error("Current password is incorrect.")
            return

        # update password
        import hashlib as _h
        db.update_user(self._user_id,
                       password_hash=_h.sha256(new_pw.encode()).hexdigest())
        self.error_lbl.setVisible(False)
        self.f_current.clear(); self.f_new.clear(); self.f_confirm.clear()
        QMessageBox.information(self, "Success", "Password changed successfully.")

    def _show_error(self, msg: str):
        """Display an error message below the password fields."""
        self.error_lbl.setText(msg)
        self.error_lbl.setVisible(True)


# ─────────────────────────────────────────────
# Top Navigation Bar
# ─────────────────────────────────────────────
class NavBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("QWidget { background: #2e7d32; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 16, 0)
        layout.setSpacing(10)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(8)
        logo_icon = QLabel()
        try:
            dino_pixmap = QPixmap(DINO_LOGO_PATH).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if dino_pixmap.isNull():
                print(f"Error: Could not load dino logo from {DINO_LOGO_PATH}")
                # ตัวสำรองหากโหลดภาพล้มเหลว
                px = QPixmap(32, 32); px.fill(Qt.transparent)
                logo_icon.setPixmap(px)
            else:
                logo_icon.setPixmap(dino_pixmap)
        except Exception as e:
            print(f"Error loading dino logo: {e}")
            px = QPixmap(32, 32); px.fill(Qt.transparent)
            logo_icon.setPixmap(px)

        logo_layout.addWidget(logo_icon)
        logo_text = QLabel("JurassiCart")
        logo_text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_text.setStyleSheet("color: white; letter-spacing: 1px;")
        logo_layout.addWidget(logo_text)
        layout.addLayout(logo_layout)
        layout.addSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("Search")
        search.setFixedHeight(36)
        search.setFont(QFont("Segoe UI", 10))
        search.setStyleSheet("""
            QLineEdit {
                background: white; border: none;
                border-radius: 5px; padding: 0 14px; color: #333;
            }
        """)
        layout.addWidget(search, stretch=1)

        btn_style = """
            QPushButton { background: transparent; color: white; border: none; }
            QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 20px; }
        """

        filter_btn = QPushButton()
        filter_btn.setFixedSize(40, 40)
        filter_btn.setCursor(Qt.PointingHandCursor)
        filter_btn.setIcon(QIcon("mdi_filter-outline.png")) 
        filter_btn.setIconSize(QSize(24, 24)) 
        filter_btn.setStyleSheet(btn_style)
        layout.addWidget(filter_btn)

        
        cart_btn = QPushButton()
        cart_btn.setFixedSize(40, 40)
        cart_btn.setCursor(Qt.PointingHandCursor)
        cart_btn.setIcon(QIcon("bx_cart.png")) 
        cart_btn.setIconSize(QSize(26, 26)) 
        cart_btn.setStyleSheet(btn_style)
        layout.addWidget(cart_btn)

       
        profile_btn = QPushButton()
        profile_btn.setFixedSize(40, 40)
        profile_btn.setCursor(Qt.PointingHandCursor)
        try:
            profile_pixmap = QPixmap(USER_AVATAR_PATH).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if profile_pixmap.isNull():
                print(f"Error: Could not load user avatar for navbar from {USER_AVATAR_PATH}")
                profile_btn.setIcon(QIcon())
            else:
                profile_btn.setIcon(QIcon(profile_pixmap))
        except Exception as e:
            print(f"Error loading user avatar for navbar: {e}")
            profile_btn.setIcon(QIcon())

        profile_btn.setIconSize(QSize(28, 28))
        profile_btn.setStyleSheet(btn_style)
        layout.addWidget(profile_btn)

# ─────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────
class AccountPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(0)

        # 🧱 การ์ดสีขาว (ตัวสำคัญ!)
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Tab + Logout (optional)
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 12, 0)

        self.tab_bar = TabBar(["My Profile", "Wallet", "Change Password"])
        top_row.addWidget(self.tab_bar)

        card_layout.addLayout(top_row)

        # เส้นคั่น
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ddd;")
        card_layout.addWidget(line)

        # Stack pages
        self.stack = QStackedWidget()
        self.stack.addWidget(ProfilePage())
        self.stack.addWidget(WalletPage())
        self.stack.addWidget(ChangePasswordPage())

        card_layout.addWidget(self.stack)

        # ใส่ card เข้า root
        root.addWidget(card)

        # connect tab
        self.tab_bar.tab_changed.connect(self.stack.setCurrentIndex)

    def load_user(self, user: dict):
        """Called by MainWindow after login to populate profile data."""
        self.stack.widget(0).load_user(user)   # ProfilePage
        self.stack.widget(1).load_user(user)   # WalletPage
        self.stack.widget(2).load_user(user)   # ChangePasswordPage