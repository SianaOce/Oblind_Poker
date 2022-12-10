import os

import python_avatars as avatar
import cairosvg
from PIL import Image, ImageQt

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QColor, QIcon
from PySide6.QtWidgets import QGraphicsView, QLabel, QHBoxLayout, QApplication, QGraphicsScene, \
    QGraphicsPixmapItem, QGridLayout, QPushButton, QComboBox, QColorDialog, QLineEdit, QDialog

from oblind.constants import CONFIG_DIR


class CreateAvatar(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Création d'Avatar")
        self.svg_temp = os.path.join(CONFIG_DIR, "temp.svg")
        self.png_temp = os.path.join(CONFIG_DIR, "temp.png")
        self.image_created = None
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.scene_avatar = QGraphicsScene()
        self.view_avatar = QGraphicsView(self.scene_avatar)

        self.label_top = QLabel("Coiffure")
        self.combo_top = QComboBox()
        self.color_hair = QComboBox()
        self.color_hat = QComboBox()

        self.label_eyeb = QLabel("Sourcils")
        self.combo_eyeb = QComboBox()

        self.label_eye = QLabel("Yeux")
        self.combo_eye = QComboBox()

        self.label_nose = QLabel("Nez")
        self.combo_nose = QComboBox()

        self.label_mouth = QLabel("Bouche")
        self.combo_mouth = QComboBox()

        self.label_facialhair = QLabel("Pilosité")
        self.combo_facialhair = QComboBox()
        self.color_facialhair = QComboBox()

        self.label_skincolor = QLabel("Couleur de peau")
        self.combo_skincolor = QComboBox()

        self.label_clothing = QLabel("Vêtement")
        self.combo_clothing = QComboBox()
        self.color_clothing = QComboBox()
        self.graph_clothing = QComboBox()
        self.line_custom_text = QLineEdit()

        self.label_acc = QLabel("Accessoire")
        self.combo_acc = QComboBox()

        self.btn = QPushButton("")

        self.update_avatar()

    def color_icon(self, rcolor):
        px = QPixmap(640, 640)
        px.fill(Qt.transparent)
        painter = QPainter(px)
        painter.setBrush(QColor(str(rcolor)))
        painter.drawEllipse(px.rect())
        painter.end()
        return px

    def modify_widgets(self):

        self.view_avatar.setRenderHints(QPainter.Antialiasing)

        hat = avatar.HatType.get_all()
        for x in range(len(hat)):
            self.combo_top.addItem(str(hat[x]), userData=hat[x])

        hair = avatar.HairType.get_all()
        for x in range(len(hair)):
            self.combo_top.addItem(str(hair[x]), userData=hair[x])

        hair_color = avatar.HairColor.get_all()
        for x in range(len(hair_color)):
            self.color_hair.addItem(QIcon(self.color_icon(hair_color[x])), "", userData=hair_color[x])
            self.color_facialhair.addItem(QIcon(self.color_icon(hair_color[x])), "", userData=hair_color[x])

        eyeb = avatar.EyebrowType.get_all()
        for x in range(len(eyeb)):
            self.combo_eyeb.addItem(str(eyeb[x]))

        eye = avatar.EyeType.get_all()
        for x in range(len(eye)):
            self.combo_eye.addItem(str(eye[x]))

        nose = avatar.NoseType.get_all()
        for x in range(len(nose)):
            self.combo_nose.addItem(str(nose[x]))

        mouth = avatar.MouthType.get_all()
        for x in range(len(mouth)):
            self.combo_mouth.addItem(str(mouth[x]))

        facial_hair = avatar.FacialHairType.get_all()
        for x in range(len(facial_hair)):
            self.combo_facialhair.addItem(str(facial_hair[x]))

        skin_c = avatar.skin_colors.SkinColor.get_all()
        for x in range(len(skin_c)):
            self.combo_skincolor.addItem(self.color_icon(skin_c[x]), "", userData=skin_c[x])

        clothing = avatar.ClothingType.get_all()
        for x in range(len(clothing)):
            self.combo_clothing.addItem(str(clothing[x]), userData=clothing[x])

        clothing_c = avatar.ClothingColor.get_all()
        for x in range(len(clothing_c)):
            self.color_clothing.addItem(self.color_icon(clothing_c[x]), "", userData=clothing_c[x])
            self.color_hat.addItem(self.color_icon(clothing_c[x]), "", userData=clothing_c[x])

        clothing_g = avatar.ClothingGraphic.get_all()
        for x in range(len(clothing_g)):
            self.graph_clothing.addItem(str(clothing_g[x]), userData=clothing_g[x])

        acc = avatar.AccessoryType.get_all()
        for x in range(len(acc)):
            self.combo_acc.addItem(str(acc[x]))

    def create_layouts(self):
        self.layout = QHBoxLayout(self)
        self.layout_2 = QGridLayout()

    def add_widgets_to_layouts(self):
        self.layout.addWidget(self.view_avatar)
        self.layout.addLayout(self.layout_2)

        self.layout_2.addWidget(self.label_top, 1, 1)
        self.layout_2.addWidget(self.combo_top, 1, 2)
        self.layout_2.addWidget(self.color_hair, 1, 3)
        self.layout_2.addWidget(self.color_hat, 1, 4)

        self.layout_2.addWidget(self.label_eyeb, 2, 1)
        self.layout_2.addWidget(self.combo_eyeb, 2, 2)

        self.layout_2.addWidget(self.label_eye, 3, 1)
        self.layout_2.addWidget(self.combo_eye, 3, 2)

        self.layout_2.addWidget(self.label_nose, 4, 1)
        self.layout_2.addWidget(self.combo_nose, 4, 2)

        self.layout_2.addWidget(self.label_mouth, 5, 1)
        self.layout_2.addWidget(self.combo_mouth, 5, 2)

        self.layout_2.addWidget(self.label_facialhair, 6, 1)
        self.layout_2.addWidget(self.combo_facialhair, 6, 2)
        self.layout_2.addWidget(self.color_facialhair, 6, 3)

        self.layout_2.addWidget(self.label_clothing, 7, 1)
        self.layout_2.addWidget(self.combo_clothing, 7, 2)
        self.layout_2.addWidget(self.color_clothing, 7, 3)
        self.layout_2.addWidget(self.graph_clothing, 7, 4)
        self.layout_2.addWidget(self.line_custom_text, 7, 5)

        self.layout_2.addWidget(self.label_skincolor, 8, 1)
        self.layout_2.addWidget(self.combo_skincolor, 8, 2)

        self.layout_2.addWidget(self.label_acc, 9, 1)
        self.layout_2.addWidget(self.combo_acc, 9, 2)

        self.layout_2.addWidget(self.btn, 10, 1, 1, 4)

    def setup_connections(self):

        self.combo_top.currentIndexChanged.connect(self.update_avatar)
        self.color_hair.currentIndexChanged.connect(self.update_avatar)
        self.color_hat.currentIndexChanged.connect(self.update_avatar)

        self.combo_eyeb.currentIndexChanged.connect(self.update_avatar)

        self.combo_eye.currentIndexChanged.connect(self.update_avatar)

        self.combo_nose.currentIndexChanged.connect(self.update_avatar)

        self.combo_mouth.currentIndexChanged.connect(self.update_avatar)

        self.combo_facialhair.currentIndexChanged.connect(self.update_avatar)
        self.color_facialhair.currentIndexChanged.connect(self.update_avatar)

        self.combo_clothing.currentIndexChanged.connect(self.update_avatar)
        self.color_clothing.currentIndexChanged.connect(self.update_avatar)
        self.graph_clothing.currentIndexChanged.connect(self.update_avatar)

        self.combo_skincolor.currentIndexChanged.connect(self.update_avatar)

        self.combo_acc.currentIndexChanged.connect(self.update_avatar)

        self.btn.clicked.connect(self.save_quit)

    def color_choice(self):
        col = QColorDialog.getColor()
        self.color_hair.setAutoFillBackground(True)
        self.color_hair.setPalette(col)

    def update_avatar(self):

        self.scene_avatar.clear()

        style = avatar.AvatarStyle.TRANSPARENT
        top = self.combo_top.currentData()
        hair_color = self.color_hair.currentData()
        hat_color = self.color_hat.currentData()
        eyebrows = str(self.combo_eyeb.currentText())
        eyes = self.combo_eye.currentText()
        nose = self.combo_nose.currentText()
        mouth = self.combo_mouth.currentText()
        facial_hair = self.combo_facialhair.currentText()
        facial_hair_color = self.color_facialhair.currentData()
        clothing = self.combo_clothing.currentData()
        clothing_color = self.color_clothing.currentData()
        shirt_graphic = self.graph_clothing.currentData()
        shirt_text = self.line_custom_text.text()
        skin_color = self.combo_skincolor.currentData()
        accessory = self.combo_acc.currentText()

        my_avat = ""
        my_avat = avatar.Avatar(style=style,
                                top=top,
                                eyebrows=eyebrows,
                                eyes=eyes,
                                nose=nose,
                                mouth=mouth,
                                facial_hair=facial_hair,
                                facial_hair_color=facial_hair_color,
                                skin_color=skin_color,
                                hair_color=hair_color,
                                hat_color=hat_color,
                                accessory=accessory,
                                clothing=clothing,
                                clothing_color=clothing_color,
                                shirt_graphic=shirt_graphic,
                                shirt_text=shirt_text)

        my_avat.render(self.svg_temp)
        cairosvg.svg2png(url=self.svg_temp, write_to=self.png_temp, parent_height=1500, parent_width=1500)
        self.file = self.png_temp
        avat = Image.open(self.file)
        self.avat_Qt = QPixmap.fromImage(ImageQt.ImageQt(avat))
        self.pix_avatar = QGraphicsPixmapItem(self.avat_Qt)
        self.scene_avatar.addItem(self.pix_avatar)

    def save_quit(self):
        self.image_created = self.png_temp
        self.close()


if __name__ == "__main__":
    app = QApplication()
    screen = app.screens()[0]
    win = CreateAvatar()
    win.show()
    app.exec()
