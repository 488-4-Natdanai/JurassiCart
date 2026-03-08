from PySide6.QtGui import QFontDatabase, QFont
import os

dir = os.path.dirname(__file__)

font_path = os.path.join(dir, "DinopiaRegular-mLrO9.otf")

font_id = QFontDatabase.addApplicationFont(font_path)

print("font_id:", font_id)

if font_id != -1:
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    print("font family:", font_family)
else:
    print("โหลดฟอนต์ไม่สำเร็จ")