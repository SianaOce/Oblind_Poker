import os
import json
import random

from PIL import Image, ImageQt

from PySide6.QtCore import QSize
from PySide6.QtGui import QBrush, Qt, QColor, QPainter, QFont, QPixmap, QPen, QIcon, QFontMetrics, QKeyEvent
from PySide6.QtWidgets import QWidget, QGridLayout, QGroupBox, QListWidget, QGraphicsScene, QLabel, \
    QComboBox, QSpinBox, QGraphicsTextItem, QDoubleSpinBox, QPushButton, QListWidgetItem, QGraphicsView, \
    QGraphicsPixmapItem, QGraphicsSimpleTextItem, QSpacerItem, QSizePolicy

from oblind.constants import CONFIG_DIR, SB_BB, ANTES, TIME_SPAN
from oblind.chips import list_chips, chip_maj_use, chip_maj_nb, chip_maj_val, chips_init_use, value_cave, \
    nbchips_cave

from oblind.bdsql import list_players_db, save_start_game_db

from oblind.timeblind import sort_sb_bb, game_structure
from oblind.gui.drawtable import Table, calc_coord
from oblind.gui import clock


# Fenetre de configuration d'une partie
class ConfigWindow(QWidget):
    def __init__(self, w, h):
        super().__init__()
        self.setWindowTitle("Paramétrage de la partie")
        self.list_players = list_players_db()
        self.list_players_seated = []
        self.res_x = w
        self.res_y = h
        self.shuffle = None

        with open(os.path.join(CONFIG_DIR, "levels.json"), "w") as write_file:
            json.dump({"Tps_Tot": 0}, write_file, indent=4)

        self.setup_ui()
        self.update_ui()
        self.move(w / 2 - self.sizeHint().width() / 2, h / 2 - self.sizeHint().height() / 2)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):

        self.player_listwidget = QListWidget()
        self.player_listwidget.setMinimumWidth(250)
        self.scene = QGraphicsScene()
        self.visuel_table = QGraphicsView(self.scene)
        self.visuel_table.setMinimumWidth(1200)
        self.visuel_table.setMinimumHeight(700)
        self.group_level = QGroupBox()

        self.verticalSpacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.label_niveau = QLabel("LvL")
        self.label_duree = QLabel("Durée")
        self.label_SB_BB = QLabel("SB / BB")
        self.label_ante = QLabel("Ante")
        self.label = []
        self.combo_duree = []
        self.combo_SB_BB = []
        self.combo_ante = []
        for i in range(1, 11):
            self.label.append(QLabel(f"{i}"))
            self.combo_duree.append(QComboBox())
            self.combo_SB_BB.append(QComboBox())
            self.combo_ante.append(QComboBox())
        self.verticalSpacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.label_total_time = QLabel()

        self.group_cave = QGroupBox()
        self.label_tpye_jeton = QLabel("Type de jeton ► ")
        self.label_value_chip = QLabel("Valeur par jeton ► ")
        self.label_nb_chip = QLabel("Nombre par joueur  ► ")
        self.label0_value_chip_by_cave = QLabel("Valeur par cave  ► ")
        self.label0_qty_chip = QLabel("Disponibles en stock ► ")

        self.combo_image_chip = []
        self.spin_nb_chip = []
        self.spin_value_chip = []
        self.label_value_chip_by_cave = []
        self.label_qty_chip = []

        for i in range(4):
            self.combo_image_chip.append(QComboBox())
            self.spin_nb_chip.append(QSpinBox())
            self.spin_value_chip.append(QSpinBox())
            self.label_value_chip_by_cave.append(QLabel())
            self.label_qty_chip.append(QLabel())

        self.label_resume_cave = QLabel()
        self.label_price = QLabel("Prix ► ")
        self.spin_buyin = QDoubleSpinBox()
        self.horizontalSpacer1 = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalSpacer2 = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontalSpacer3 = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.start_btn = QPushButton("Start")

    def modify_widgets(self):

        self.visuel_table.setRenderHints(QPainter.Antialiasing)

        for i in self.list_players:
            item_player = QListWidgetItem(f"{self.list_players[i]['lastname']} {self.list_players[i]['name']}")
            item_player.setData(Qt.UserRole, i)
            self.player_listwidget.addItem(item_player)

        self.label_niveau.setAlignment(Qt.AlignCenter)
        self.label_duree.setAlignment(Qt.AlignCenter)
        self.label_SB_BB.setAlignment(Qt.AlignCenter)
        self.label_ante.setAlignment(Qt.AlignCenter)

        for i in range(0, 10):
            self.label[i].setAlignment(Qt.AlignCenter)
            self.combo_duree[i].addItems(TIME_SPAN)
            self.combo_duree[i].setMinimumWidth(70)
            self.combo_SB_BB[i].addItem("")
            self.combo_SB_BB[i].addItems(SB_BB[i:])
            self.combo_SB_BB[i].setMinimumWidth(160)
            self.combo_ante[i].addItems(ANTES)
            self.combo_ante[i].setMinimumWidth(70)

            if i > 0:
                self.combo_SB_BB[i].setEnabled(False)
                self.combo_duree[i].setEnabled(False)
                self.combo_ante[i].setEnabled(False)

        for i in range(4):

            for key, item in list_chips().items():
                self.combo_image_chip[i].setIconSize(QSize(60, 60))
                self.combo_image_chip[i].setMinimumHeight(80)
                self.combo_image_chip[i].setMaximumWidth(180)
                ic = QIcon(os.path.join(CONFIG_DIR, f"{key}.png"))
                self.combo_image_chip[i].addItem(ic, key)

            self.combo_image_chip[i].addItem("-")
            self.combo_image_chip[i].setCurrentIndex(self.combo_image_chip[i].count() - 1)
            self.spin_nb_chip[i].setRange(0, 100)
            self.spin_nb_chip[i].setAlignment(Qt.AlignCenter)
            self.spin_value_chip[i].setRange(0, 1000)
            self.spin_value_chip[i].setAlignment(Qt.AlignCenter)

        self.spin_buyin.setRange(0, 100)
        self.spin_buyin.setSingleStep(0.5)
        self.spin_buyin.setSuffix(" €")
        self.spin_buyin.setAlignment(Qt.AlignCenter)

        self.load_infochip()

        self.start_btn.setEnabled(False)

    def create_layouts(self):
        self.layout_window = QGridLayout(self)
        self.layout_blind_structure = QGridLayout(self.group_level)
        self.layout_blind_structure.setVerticalSpacing(5)
        self.layout_cave_chips = QGridLayout(self.group_cave)

    def add_widgets_to_layouts(self):

        self.layout_window.addWidget(self.player_listwidget, 1, 1, 1, 1)
        self.layout_window.addWidget(self.visuel_table, 1, 2, 1, 1)
        self.layout_window.addWidget(self.group_level, 1, 3, 1, 1)
        self.layout_blind_structure.addItem(self.verticalSpacer1, 1, 1, 1, 4)
        self.layout_blind_structure.addWidget(self.label_niveau, 2, 1, 1, 1)
        self.layout_blind_structure.addWidget(self.label_duree, 2, 2, 1, 1)
        self.layout_blind_structure.addWidget(self.label_SB_BB, 2, 3, 1, 1)
        self.layout_blind_structure.addWidget(self.label_ante, 2, 4, 1, 1)
        for i in range(0, 10):
            self.layout_blind_structure.addWidget(self.label[i], i + 3, 1, 1, 1)
            self.layout_blind_structure.addWidget(self.combo_duree[i], i + 3, 2, 1, 1)
            self.layout_blind_structure.addWidget(self.combo_SB_BB[i], i + 3, 3, 1, 1)
            self.layout_blind_structure.addWidget(self.combo_ante[i], i + 3, 4, 1, 1)
        self.layout_blind_structure.addItem(self.verticalSpacer2, 13, 1, 1, 4)
        self.layout_blind_structure.addWidget(self.label_total_time, 14, 1, 1, 4, Qt.AlignVCenter | Qt.AlignCenter)

        self.layout_window.addWidget(self.group_cave, 2, 1, 1, 2)
        self.layout_cave_chips.addItem(self.horizontalSpacer1, 1, 1, 1, 1)
        self.layout_cave_chips.addWidget(self.label_tpye_jeton, 1, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)
        self.layout_cave_chips.addWidget(self.label_nb_chip, 2, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)
        self.layout_cave_chips.addWidget(self.label_value_chip, 3, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)
        self.layout_cave_chips.addWidget(self.label0_value_chip_by_cave, 4, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)
        self.layout_cave_chips.addWidget(self.label0_qty_chip, 5, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)

        for i in range(0, 4):
            self.layout_cave_chips.addWidget(self.combo_image_chip[i], 1, i + 3, 1, 1)
            self.layout_cave_chips.addWidget(self.spin_nb_chip[i], 2, i + 3, 1, 1)
            self.layout_cave_chips.addWidget(self.spin_value_chip[i], 3, i + 3, 1, 1)
            self.layout_cave_chips.addWidget(self.label_value_chip_by_cave[i], 4, i + 3, 1, 1,
                                             Qt.AlignVCenter | Qt.AlignCenter)
            self.layout_cave_chips.addWidget(self.label_qty_chip[i], 5, i + 3, 1, 1, Qt.AlignVCenter | Qt.AlignCenter)

        self.layout_cave_chips.addItem(self.horizontalSpacer2, 1, 7, 1, 1)
        self.layout_cave_chips.addWidget(self.label_resume_cave, 1, 8, 3, 1, Qt.AlignVCenter | Qt.AlignLeft)
        self.layout_cave_chips.addWidget(self.spin_buyin, 4, 8, 1, 1, Qt.AlignVCenter | Qt.AlignLeft)
        self.layout_cave_chips.addItem(self.horizontalSpacer3, 1, 9, 4, 1)

        self.layout_window.addWidget(self.start_btn, 2, 3, 1, 1)

    def setup_connections(self):

        self.player_listwidget.itemDoubleClicked.connect(self.add_player_sel)

        for i in range(0, 10):
            self.combo_SB_BB[i].currentIndexChanged.connect(self.update_level)
            self.combo_duree[i].currentIndexChanged.connect(self.update_level)

        self.combo_image_chip[0].currentIndexChanged.connect(self.selectchip_change1)
        self.combo_image_chip[1].currentIndexChanged.connect(self.selectchip_change2)
        self.combo_image_chip[2].currentIndexChanged.connect(self.selectchip_change3)
        self.combo_image_chip[3].currentIndexChanged.connect(self.selectchip_change4)

        for x in range(4):
            self.spin_nb_chip[x].valueChanged.connect(self.combo_nb)
            self.spin_value_chip[x].valueChanged.connect(self.combo_val)

        self.spin_buyin.valueChanged.connect(self.update_buyin)

        self.start_btn.clicked.connect(self.start_game)

    def add_player_sel(self):

        nb_players_seat = len([self.list_players[x] for x in self.list_players if self.list_players[x]["seated"]])

        if nb_players_seat <= 9:
            self.list_players[self.player_listwidget.currentItem().data(Qt.UserRole)]["seated"] = True
            self.update_ui()

        self.player_listwidget.currentItem().setSelected(False)

    def update_level(self):

        levels = []

        for i in range(0, 10):
            levels.append([self.combo_duree[i].currentIndex(),
                           self.combo_SB_BB[i].currentIndex(),
                           self.combo_ante[i].currentIndex()])
        levels, n = sort_sb_bb(levels)

        for i in range(0, 10):
            self.combo_duree[i].setCurrentIndex(levels[i][0])
            self.combo_SB_BB[i].setCurrentIndex(levels[i][1])
            self.combo_duree[i].setEnabled(i <= n)
            self.combo_SB_BB[i].setEnabled(self.combo_duree[i].currentIndex() != 0)
            self.combo_ante[i].setEnabled(self.combo_duree[i].currentIndex() != 0)

        with open(os.path.join(CONFIG_DIR, "levels.json"), "w") as write_file:
            json.dump(game_structure(levels), write_file, indent=4)

        self.update_ui()

        return levels

    def del_player(self, id_player):

        self.list_players[id_player]["seated"] = False
        self.update_ui()

    def update_buyin(self):

        self.update_ui()

    def update_ui(self):

        with open(os.path.join(CONFIG_DIR, "levels.json"), "r") as read_file:
            time = json.load(read_file)["Tps_Tot"]

        t_tot = f"{time // 60}h{time % 60:02}min"

        cave = value_cave()

        self.scene.clear()

        self.w = 1148
        self.h = self.w / 2
        r = 0.6 * self.w / 4

        self.scene.setSceneRect(0, 0, self.w, self.h)

        positions_jeton = calc_coord(0.70 * r, r, 0)
        positions_avatar = calc_coord(1.52 * r, r, 0)

        table = Table(self.w, 0.6)

        self.scene.addItem(table)

        pos = 0
        im = []

        font1 = QFont('Roboto', 20)
        metrics_font1 = QFontMetrics(font1)

        self.list_players_seated = []

        for id_player, player_seat in [(x, self.list_players[x]) for x in self.list_players if
                                       self.list_players[x]["seated"]]:
            self.list_players_seated.append((id_player, player_seat))

        if self.shuffle:
            random.shuffle(self.list_players_seated)
        self.shuffle = None

        for id_player, player_seat in self.list_players_seated:

            self.text_jeton = QGraphicsSimpleTextItem(cave, parent=table)
            self.text_jeton.setBrush(QColor("#e1e1ff"))
            self.text_jeton.setFont(font1)
            decal_y = 0
            if pos > 5:
                decal_y = 30

            self.text_jeton.setPos(
                self.w / 2 - r * 2 + positions_jeton[str(pos)][0] - metrics_font1.boundingRect(cave).width() / 2,
                self.h / 2 - r + positions_jeton[str(pos)][1] - metrics_font1.height() / 2 + decal_y)
            d = int(self.w / 12)

            im_chips = Image.open("resources/pilecave.png")
            im_chips = im_chips.resize((30, 30))
            im_chips_Qt = QPixmap.fromImage(ImageQt.ImageQt(im_chips))
            self.image_chip = QGraphicsPixmapItem(im_chips_Qt, parent=self.text_jeton)
            self.image_chip.setPos(15, -30)

            if os.path.isfile(os.path.join(CONFIG_DIR, player_seat["avatar"])):
                avatar = Image.open(os.path.join(CONFIG_DIR, player_seat["avatar"]))
                avatar = avatar.resize((d, d))
                avatar_Qt = QPixmap.fromImage(ImageQt.ImageQt(avatar))
                self.pix_avatar = self.Avatar(avatar_Qt, id_player, self)
            else:
                im.append(QPixmap(d, d))
                im[-1].fill(QColor(0, 0, 0, 1))
                p = QPainter(im[-1])
                p.setRenderHints(QPainter.Antialiasing)
                p.setPen(QPen(QColor("#80135b")))
                p.setBrush(QBrush(QColor("#80135b")))
                p.drawEllipse(0, 0, d, d)
                p.end()
                self.pix_avatar = self.Avatar(im[-1], id_player, self)
            gap_y = 0
            if pos > 5:
                gap_y = metrics_font1.height()
            self.pix_avatar.setParentItem(table)
            self.pix_avatar.setPos(int(self.w / 2 - r * 2) + positions_avatar[f"{pos}"][0] - d / 2,
                                   int(self.h / 2 - r) + positions_avatar[f"{pos}"][1] - d / 2 - gap_y)
            self.text_prenom = QGraphicsSimpleTextItem(player_seat["lastname"], parent=table)
            self.text_prenom.setBrush(QColor("#e1e1ff"))
            self.text_prenom.setFont(font1)
            self.text_prenom.setPos(self.w / 2 - r * 2 + positions_avatar[str(pos)][0] - metrics_font1.boundingRect(
                player_seat["lastname"]).width() / 2, self.h / 2 - r + positions_avatar[str(pos)][
                                        1] - metrics_font1.height() / 10 + d / 2 - gap_y)
            pos += 1

        list_chips_use = ([[key] for key, item in list_chips().items() if item['n_use'] != 0])

        for x in range(4):
            k = self.combo_image_chip[x].currentText()
            v = list_chips().get(k)
            if v:
                self.label_qty_chip[x].setText(str(v["qty_total"] - v["qty_use"] * len(self.list_players_seated)))
                self.label_value_chip_by_cave[x].setText(str(v["value"] * v["qty_use"]))
            else:
                self.label_qty_chip[x].setText("-")
                self.label_value_chip_by_cave[x].setText("-")

        self.label_total_time.setText(f"Durée de la partie ► {t_tot}")
        self.label_resume_cave.setText(f"<h2 align=\"center\"><b><u>Cave</u></b></h2>"
                                       f"<div>Valeur ► {cave}<br>"
                                       f"Nombre de jetons ► {nbchips_cave()}<br>"
                                       f"Type de jeton ► {len(list_chips_use)}<br>"
                                       f"Prix ▼ </div>"
                                       )

        # Mise à jour item dans
        for x in range(self.player_listwidget.count()):
            if self.player_listwidget.item(x).data(Qt.UserRole) in [z for z, y in self.list_players_seated]:
                self.player_listwidget.item(x).setHidden(True)
            else:
                self.player_listwidget.item(x).setHidden(False)
        # Verification condition necessaire aux demarrage de la partie (deverouillage bouton)
        if len(self.list_players_seated) > 1 and \
                self.spin_buyin.value() != 0 and \
                self.combo_duree[0].currentIndex() != 0 and \
                self.combo_SB_BB[0].currentIndex() != 0:

            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

    def load_infochip(self):

        for key, item in list_chips().items():
            if item["n_use"] != 0:
                self.combo_image_chip[item["n_use"] - 1].setCurrentText(key)
                self.spin_nb_chip[item["n_use"] - 1].setValue(item["qty_use"])
                self.spin_value_chip[item["n_use"] - 1].setValue(item["value"])
                self.spin_nb_chip[item["n_use"] - 1].setEnabled(True)
                self.spin_value_chip[item["n_use"] - 1].setEnabled(True)

        for i in range(4):
            if self.combo_image_chip[i].currentIndex() == self.combo_image_chip[i].count() - 1:
                self.spin_nb_chip[i].setValue(0)
                self.spin_nb_chip[i].setEnabled(False)
                self.spin_value_chip[i].setValue(0)
                self.spin_value_chip[i].setEnabled(False)

    def selectchip_change1(self):
        self.selectchip(0)

    def selectchip_change2(self):
        self.selectchip(1)

    def selectchip_change3(self):
        self.selectchip(2)

    def selectchip_change4(self):
        self.selectchip(3)

    def selectchip(self, act_combo):

        # Deselectionne le jeton choisi si selectionné dans un autre combobox
        for j in range(4):
            if self.combo_image_chip[j].currentText() == self.combo_image_chip[
                act_combo].currentText() and act_combo != j:
                self.combo_image_chip[j].setCurrentIndex(self.combo_image_chip[j].count() - 1)

        chips_init_use()

        # Sauvegarde
        for i in range(4):
            if self.combo_image_chip[i].currentText() != "-":
                name = self.combo_image_chip[i].currentText()
                n = i + 1
                chip_maj_use(name, n)

        self.load_infochip()
        self.update_ui()

    def combo_nb(self):

        for i in range(4):
            name = self.combo_image_chip[i].currentText()
            nb = self.spin_nb_chip[i].value()
            chip_maj_nb(name, nb)

        self.update_ui()

    def combo_val(self):

        for i in range(4):
            name = self.combo_image_chip[i].currentText()
            val = self.spin_value_chip[i].value()
            chip_maj_val(name, val)

        self.update_ui()

    def start_game(self):

        buy_in = self.spin_buyin.value()
        chips = value_cave()
        list_player = [x for x, y in self.list_players_seated]
        blinds = self.update_level()
        structure = game_structure(blinds)

        id_game = save_start_game_db(buy_in, chips, list_player)

        with open(os.path.join(CONFIG_DIR, f"{id_game}.json"), "w") as write_file:
            json.dump(structure, write_file, indent=4)

        self.window_chrono = clock.ChronoWindow(id_game=id_game, w=self.res_x, h=self.res_y)
        self.window_chrono.setWindowModality(Qt.ApplicationModal)
        self.window_chrono.showMaximized()

    def keyPressEvent(self, event: QKeyEvent) -> None:

        if event.key() == 32:
            self.shuffle = True
            self.update_ui()

    class Avatar(QGraphicsPixmapItem):

        def __init__(self, pixmap, id_player=None, instance=None):
            super().__init__(pixmap)
            self.id_player = id_player
            self.instance = instance

        def __str__(self):
            return str(self.id_player)

        def mouseDoubleClickEvent(self, e):
            self.instance.del_player(id_player=self.id_player)
