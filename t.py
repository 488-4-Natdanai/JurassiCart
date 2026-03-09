from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication
import os
import sys

# Create QApplication if it doesn't exist
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

dir = os.path.dirname(__file__)

font_path = os.path.join(dir, "DinopiaRegular-mLrO9.otf")

font_id = QFontDatabase.addApplicationFont(font_path)

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