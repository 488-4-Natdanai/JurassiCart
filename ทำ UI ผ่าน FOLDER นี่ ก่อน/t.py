import sys
import os
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QFontDatabase, QFont

app = QApplication(sys.argv)

dir = os.path.dirname(__file__)
font_path = os.path.join(dir, "DinopiaRegular-mLrO9.otf")
font_id = QFontDatabase.addApplicationFont(font_path)
font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
print("font_id =", font_id)

label = QLabel("JurassiCart")
label.show()
app.setFont(QFont(font_family, 12))
sys.exit(app.exec())