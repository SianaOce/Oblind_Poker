import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir
from PySide6.QtGui import QIcon

from oblind.gui.mainmenu import MainWindow

QDir.addSearchPath("icon", "theme")
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("resources/icone_clink.ico"))
with open("dark_blue.qss", "r") as file:
    _style = file.read()
    app.setStyleSheet(_style)

screen = app.screens()[0]
win = MainWindow(screen.size().width(), screen.size().height())
win.show()
app.exec()
