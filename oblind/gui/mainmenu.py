from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSpacerItem
from PySide6.QtGui import QPixmap

import cairosvg

from oblind.gui import results, settings, gameconfig


class MainWindow(QWidget):
    def __init__(self, w, h):
        super().__init__()
        self.res_x = w
        self.res_y = h
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setup_ui()
        self.move(w / 2 - self.sizeHint().width() / 2, h / 2 - self.sizeHint().height() / 2)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.horizontal_spacer0 = QSpacerItem(10, 25)
        self.lbl_logo = QLabel()
        self.lbl_title = QLabel()
        self.horizontal_spacer1 = QSpacerItem(10, 75)
        self.btn_start = QPushButton("Démarrer partie")
        self.btn_settings = QPushButton("Paramètres")
        self.btn_stats = QPushButton("Résultats")
        self.btn_quit = QPushButton("Quitter")
        self.horizontal_spacer2 = QSpacerItem(10, 100)
        self.lbl_about_logo = QLabel()
        self.lbl_about_txt = QLabel()

    def modify_widgets(self):
        cairosvg.svg2png(url="resources/icone_clink.svg", write_to="resources/icone_clink.png")
        logo = QPixmap("resources/icone_clink.png")
        self.lbl_logo.setPixmap(logo)
        self.lbl_logo.setAlignment(Qt.AlignCenter)

        self.lbl_title.setText("<u>O'blind Poker</u>")
        self.lbl_title.setStyleSheet("font-size: 44px")
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.btn_start.setStyleSheet("height: 75px")

        about = QPixmap("resources/SE.png")
        self.lbl_about_logo.setPixmap(about)

        self.lbl_about_logo.setAlignment(Qt.AlignRight)
        self.lbl_about_txt.setText("<i> 14 mars 2023 v1.1.0 </i>")
        self.lbl_about_txt.setStyleSheet("font-size: 14px")
        self.lbl_about_txt.setAlignment(Qt.AlignRight)

    def create_layouts(self):
        self.layout1 = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.layout1.addSpacerItem(self.horizontal_spacer0)
        self.layout1.addWidget(self.lbl_logo)
        self.layout1.addWidget(self.lbl_title)
        self.layout1.addItem(self.horizontal_spacer1)
        self.layout1.addWidget(self.btn_start)
        self.layout1.addWidget(self.btn_settings)
        self.layout1.addWidget(self.btn_stats)
        self.layout1.addWidget(self.btn_quit)
        self.layout1.addItem(self.horizontal_spacer2)
        self.layout1.addWidget(self.lbl_about_logo)
        self.layout1.addWidget(self.lbl_about_txt)

    def setup_connections(self):
        self.btn_start.clicked.connect(self.start)
        self.btn_settings.clicked.connect(self.settings)
        self.btn_stats.clicked.connect(self.stats)
        self.btn_quit.clicked.connect(self.close)

    def start(self):
        self.window_start = gameconfig.ConfigWindow(self.res_x, self.res_y)
        self.window_start.setWindowModality(Qt.ApplicationModal)
        self.window_start.showMaximized()

    def settings(self):
        self.window_settings = settings.MainWindow()
        self.window_settings.setWindowModality(Qt.ApplicationModal)
        self.window_settings.show()

    def stats(self):
        self.window_results = results.MainWindow(None)
        self.window_results.setWindowModality(Qt.ApplicationModal)
        self.window_results.showMaximized()
