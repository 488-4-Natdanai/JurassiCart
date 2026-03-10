<<<<<<< Updated upstream
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication
import os
import sys

# Create QApplication if it doesn't exist
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)
=======
import sys
import os
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QFontDatabase, QFont

app = QApplication(sys.argv)
>>>>>>> Stashed changes

dir = os.path.dirname(__file__)
font_path = os.path.join(dir, "DinopiaRegular-mLrO9.otf")

font_id = QFontDatabase.addApplicationFont(font_path)
font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
print("font_id =", font_id)

<<<<<<< Updated upstream
print("font_id:", font_id)

if font_id != -1:
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    print("font family:", font_family)
else:
    print("โหลดฟอนต์ไม่สำเร็จ")

if font_id != -1:
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    print("font family:", font_family)
else:
    print("โหลดฟอนต์ไม่สำเร็จ")
=======
label = QLabel("JurassiCart")
label.show()
app.setFont(QFont(font_family, 12))
sys.exit(app.exec())
>>>>>>> Stashed changes
