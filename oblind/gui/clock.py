import json
import os
from datetime import timedelta
from math import pi, cos, sin

from PIL import Image, ImageQt
from PySide6.QtCore import Qt, QTimerEvent, QBasicTimer
from PySide6.QtWidgets import QWidget, QGraphicsScene, QVBoxLayout, QSpinBox, QPushButton, \
    QGraphicsTextItem, QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem, QMessageBox, QSizePolicy
from PySide6.QtGui import QColor, QPainter, QFont, QPen, QPixmap, QBrush, QFontMetrics, QKeyEvent, QMouseEvent, QCursor, \
    QIcon

from oblind.constants import CONFIG_DIR
from oblind.gui.drawtable import Table, calc_coord
from oblind.gui import results
from oblind.bdsql import save_result_db, list_players_game, cave_info, list_players_db, save_add_cave
from oblind.chips import list_chips


class ChronoWindow(QWidget):

    def __init__(self, id_game, w, h):
        super().__init__()
        self.id_game = id_game
        self.setWindowFlags(Qt.FramelessWindowHint)

        with open(os.path.join(CONFIG_DIR, f"{self.id_game}.json")) as json_file:
            self.struct = json.load(json_file)

        self.w = 1900
        self.h = 1020

        self.font_pts_recave = QFont('TSCu_Comic', 32)
        self.metrics_pts_recave = QFontMetrics(self.font_pts_recave)

        self.nb_lvl = self.struct["Nb_Lvl"]
        self.time_t = timedelta(minutes=self.struct["Tps_Tot"])

        self.time0 = 0
        self.time1 = 0
        self.level = 0
        self.setup_ui()

        self.time_step = 100
        self.game_progress = True

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("#121212"))
        self.graph_window = QGraphicsView(self.scene)
        self.timer = QBasicTimer()

    def modify_widgets(self):
        self.display_timer(init=True)
        self.graph_window.setRenderHints(QPainter.Antialiasing)

    def create_layouts(self):
        self.layout = QVBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.layout.addWidget(self.graph_window)

    def setup_connections(self):
        pass

    def display_timer(self, init):

        [pen_back_circle1, pen_circle1, pen_back_circle2, pen_circle2] = QPen(), QPen(), QPen(), QPen()
        pen_back_circle1.setColor("#2b3b37")
        pen_circle1.setColor("#1de9b6")
        pen_back_circle2.setColor("#544c5c")
        pen_circle2.setColor("#861de9")
        pen_back_circle1.setWidth(10)
        pen_circle1.setWidth(5)
        pen_back_circle2.setWidth(5)
        pen_circle2.setWidth(2)

        font_blind = QFont('TSCu_Comic', 96)
        metrics_blind = QFontMetrics(font_blind)
        font_timeblind = QFont('TSCu_Comic', 172)
        metrics_timeblind = QFontMetrics(font_timeblind)
        font_nextblind = QFont('TSCu_Comic', 40)
        metrics_nextblind = QFontMetrics(font_nextblind)
        font_gametime = QFont('TSCu_Comic', 88)
        metrics_gametime = QFontMetrics(font_gametime)

        if init:

            # Indicateur de pause
            logo_pause = "Pause"
            self.logo_pause = QGraphicsTextItem(logo_pause)
            self.logo_pause.setDefaultTextColor(QColor("#bd094b"))
            self.logo_pause.setFont(font_nextblind)
            w_logo_pause = metrics_nextblind.boundingRect(logo_pause).width()
            h_logo_pause = metrics_blind.height()
            self.logo_pause.setPos(self.w / 2 - w_logo_pause / 2, self.h / 3)

            self.scene.addItem(self.logo_pause)

            # -----------"Progress circular" temps de blind----------------------------------------

            # Ellipse de fond

            back_circle1 = QGraphicsEllipseItem(self.w / 2 - self.h / 2, 0, self.h + 3, self.h + 3)
            back_circle1.setPen(pen_back_circle1)
            self.scene.addItem(back_circle1)

            # Remplissage par addition de petit rond

            rayon1 = self.h / 2 + 1.5
            theta1 = 1.5 * pi

            self.list_circle1 = []
            for i in range(3001):
                theta1 += 2 * pi / 3000
                x = self.w / 2 + rayon1 * cos(theta1)
                y = self.h / 2 + rayon1 * sin(theta1)
                circle1 = QGraphicsEllipseItem(x, y, 3, 3)
                circle1.setVisible(False)
                circle1.setPen(pen_circle1)
                circle1.setBrush(QColor("#1de9b6"))
                self.list_circle1.append(circle1)
                self.scene.addItem(self.list_circle1[i])

            # -----------Affichage du texte de blind en cours----------------------------------------
            blind = str(self.struct[f"lvl_{1}"][1])
            if self.struct[f"lvl_{1}"][2] != "":
                blind += " (" + str(self.struct[f"lvl_{1}"][2]) + ")"
            self.text_blind = QGraphicsTextItem(blind)
            self.text_blind.setDefaultTextColor(QColor("#1de9b6"))
            self.text_blind.setFont(font_blind)
            w_text_blind1 = metrics_blind.boundingRect(blind).width()
            h_text_blind1 = metrics_blind.height()
            self.text_blind.setPos(self.w / 2 - w_text_blind1 / 2, self.h / 2 - h_text_blind1 / 2)
            self.scene.addItem(self.text_blind)

            # Affichage du texte du temps restant de la blind en cours------------------------
            text_timeblind = str(timedelta(minutes=self.struct[f"lvl_{1}"][0]))

            self.text_timeblind = QGraphicsTextItem(text_timeblind)
            self.text_timeblind.setDefaultTextColor(QColor("#1de9b6"))
            self.text_timeblind.setFont(font_timeblind)
            w_text_timeblind = metrics_timeblind.boundingRect(text_timeblind).width()
            h_text_timeblind = metrics_timeblind.height()
            self.text_timeblind.setPos(self.w / 2 - w_text_timeblind / 2,
                                       self.h / 2 - h_text_timeblind / 2 - self.h / 4)
            self.scene.addItem(self.text_timeblind)

            # Affichage du texte de la prochaine blind----------------------------------------
            nextblind = ""
            if self.nb_lvl > 1:
                nextblind += str(timedelta(minutes=self.struct[f"lvl_{2}"][0])) + "  " + str(self.struct[f"lvl_{2}"][1])
                if self.struct[f"lvl_{2}"][2] != "":
                    nextblind += " (" + str(self.struct[f"lvl_{2}"][2]) + ")"

            self.text_nextblind = QGraphicsTextItem(nextblind)
            self.text_nextblind.setDefaultTextColor(QColor("#1de9b6"))
            self.text_nextblind.setOpacity(0.8)

            w_nextblind = metrics_nextblind.boundingRect(nextblind).width()
            h_nextblind = metrics_nextblind.height()
            self.text_nextblind.setFont(font_nextblind)
            self.text_nextblind.setPos(self.w / 2 - w_nextblind / 2, self.h / 2 - h_nextblind / 2 + self.h / 4)
            self.scene.addItem(self.text_nextblind)

            if self.nb_lvl > 1:

                # -----------"Progress circular" temps total----------------------------------------
                back_circle2 = QGraphicsEllipseItem(9 * self.w / 10 - self.h / 6, self.h / 5 - self.h / 6,
                                                    self.h / 3 + 2,
                                                    self.h / 3 + 2)
                back_circle2.setPen(pen_back_circle2)
                self.scene.addItem(back_circle2)

                rayon2 = self.h / 6 + 1
                theta2 = 1.5 * pi

                self.list_circle2 = []
                for i in range(3001):
                    theta2 += 2 * pi / 3000
                    x = 9 * self.w / 10 + rayon2 * cos(theta2)
                    y = self.h / 5 + rayon2 * sin(theta2)
                    circle2 = QGraphicsEllipseItem(x, y, 2, 2)
                    circle2.setPen(pen_circle2)
                    circle2.setVisible(False)
                    self.list_circle2.append(circle2)
                    self.scene.addItem(self.list_circle2[i])

                # -----------Affichage du texte du temps restant total
                text_gametime = str(self.time_t)

                self.text_gametime = QGraphicsTextItem(text_gametime)
                self.text_gametime.setDefaultTextColor(QColor("#861de9"))

                w_text_gametime = metrics_gametime.boundingRect(text_gametime).width()
                h_text_gametime = metrics_gametime.height()
                self.text_gametime.setFont(font_gametime)
                self.text_gametime.setPos(9 * self.w / 10 - w_text_gametime / 2, self.h / 5 - h_text_gametime / 2)
                self.scene.addItem(self.text_gametime)

            # -----------Affichage jetons
            chips_use = [[f"{key}.png", item['value']] for key, item in list_chips().items() if item['n_use'] != 0]
            sort_chips_use = sorted(chips_use, key=lambda val: val[1])

            pos = 955 - len(sort_chips_use) * 85
            for j in sort_chips_use:
                self.image_jeton = QGraphicsPixmapItem(
                    QPixmap(os.path.join(CONFIG_DIR, j[0])).scaled(150, 150, mode=Qt.SmoothTransformation))
                self.image_jeton.setPos(10, pos)
                self.scene.addItem(self.image_jeton)
                pos += 85

            pos = 1000 - len(sort_chips_use) * 85
            for i in sort_chips_use:
                self.val_jeton = QGraphicsTextItem(str(i[1]))
                self.val_jeton.setFont(font_nextblind)
                self.val_jeton.setDefaultTextColor(QColor("#861de9"))
                self.val_jeton.setPos(170, pos)
                self.scene.addItem(self.val_jeton)
                pos += 85

            self.scene.setSceneRect(0, 0, self.w, self.h)

            # -----------Affichage joueurs si recave possible
            if cave_info(self.id_game)[4]:
                self.avatar = []
                self.pts_recave = []

                list_j = list_players_game(self.id_game)

                size = 110 - 5 * len(list_j)
                pos2 = 1890 - len(list_j) * (size + 2)

                for x in range(len(list_j)):
                    self.pts_recave.append(QGraphicsTextItem())
                    self.pts_recave[x].setPlainText("'" * (list_j[x][3] + 1))
                    self.pts_recave[x].setDefaultTextColor(QColor("#861de9"))
                    self.pts_recave[x].setFont(self.font_pts_recave)
                    self.pts_recave[x].setPos(pos2, 1010)
                    self.scene.addItem(self.pts_recave[x])

                    self.avatar.append(self.CaveAvatar(
                        QPixmap(os.path.join(CONFIG_DIR, list_players_db()[list_j[x][0]]["avatar"])).scaled(
                            size, size, mode=Qt.SmoothTransformation), list_j[x], self.id_game, self.pts_recave[x]
                    ))
                    self.avatar[x].setPos(pos2, 1010 - size)
                    self.scene.addItem(self.avatar[x])

                    pos2 += size + 2

        else:

            # Mise à jour temps/circular bar
            if self.time0 == 0:
                for i in range(3001):
                    self.list_circle1[i].setVisible(False)

                blind = str(self.struct[f"lvl_{self.level + 1}"][1])
                if self.struct[f"lvl_{self.level + 1}"][2] != "":
                    blind += " (" + str(self.struct[f"lvl_{self.level + 1}"][2]) + ")"

                w_text_blind1 = metrics_blind.boundingRect(blind).width()
                h_text_blind1 = metrics_blind.height()
                self.text_blind.setPos(self.w / 2 - w_text_blind1 / 2, self.h / 2 - h_text_blind1 / 2)
                self.text_blind.setPlainText(blind)

                nextblind = ""
                if self.level + 1 < self.nb_lvl:

                    nextblind += str(timedelta(minutes=self.struct[f"lvl_{self.level + 2}"][0])) + "  " + str(
                        self.struct[f"lvl_{self.level + 2}"][1])
                    if self.struct[f"lvl_{self.level + 2}"][2] != "":
                        nextblind += " (" + str(self.struct[f"lvl_{self.level + 2}"][2]) + ")"

                w_nextblind = metrics_nextblind.boundingRect(nextblind).width()
                h_nextblind = metrics_nextblind.height()
                self.text_nextblind.setPos(self.w / 2 - w_nextblind / 2, self.h / 2 - h_nextblind / 2 + self.h / 4)
                self.text_nextblind.setPlainText(nextblind)

            else:

                rep_pre1 = int(3000 * timedelta(seconds=self.time0 - self.time_step / 1000) /
                               timedelta(minutes=self.struct[f"lvl_{self.level + 1}"][0]))
                new_rep1 = int(3000 * timedelta(seconds=self.time0) /
                               timedelta(minutes=self.struct[f"lvl_{self.level + 1}"][0]))

                for i in range(rep_pre1, new_rep1):
                    self.list_circle1[i].setVisible(True)

            rep_pre2 = int(3000 * timedelta(seconds=self.time1 - self.time_step / 1000) / self.time_t)
            new_rep2 = int(3000 * timedelta(seconds=self.time1) / self.time_t)

            self.text_timeblind.setPlainText(
                str(timedelta(minutes=self.struct[f"lvl_{self.level + 1}"][0])
                    - timedelta(seconds=int(self.time0 + self.time_step / 1000))))
            if self.nb_lvl > 1:
                for i in range(rep_pre2, new_rep2):
                    self.list_circle2[i].setVisible(True)
                self.text_gametime.setPlainText(
                    str(self.time_t - timedelta(seconds=int(self.time1 + self.time_step / 1000))))

    def timerEvent(self, event: QTimerEvent) -> None:

        if timedelta(seconds=int(self.time0 + self.time_step / 1000)) < timedelta(
                minutes=self.struct[f"lvl_{self.level + 1}"][0]):
            self.time0 += self.time_step / 1000
            self.time1 += self.time_step / 1000

            self.display_timer(init=False)
        elif self.level + 1 < self.nb_lvl:
            self.time0 = -0.1
            self.level += 1
            self.display_timer(init=False)
        else:
            self.timer.stop()
            self.game_progress = False
            self.scene_score()

    def scene_score(self):

        list_j = list_players_game(self.id_game)

        self.scene.clear()

        self.scene.setBackgroundBrush(QColor("#31363b"))

        self.w_s = 1800
        self.h_s = self.w_s / 2
        r = 0.6 * self.w_s / 4

        table = Table(self.w_s, 0.6)
        self.scene.addItem(table)

        coord_score = calc_coord(0.75 * r, r, 0)
        coord_avatar = calc_coord(1.35 * r, r, 0)

        font1 = QFont('Arial', int(self.w_s / 75))
        metrics1 = QFontMetrics(font1)

        self.font2 = QFont('Arial', int(self.w_s / 50))
        self.metrics2 = QFontMetrics(self.font2)

        self.chip_max = int(cave_info(self.id_game)[1]) * len(list_j)
        if cave_info(self.id_game)[4]:
            nb_cave = sum([x[3] for x in list_j])
            self.chip_max += int(cave_info(self.id_game)[1]) * nb_cave

        im = []
        self.spin_score = {}

        for x in range(len(list_j)):

            self.spin_score[list_j[x][0]] = QSpinBox()
            self.spin_score[list_j[x][0]].setObjectName("spinscore")
            self.spin_score[list_j[x][0]].setRange(0, self.chip_max)
            self.spin_score[list_j[x][0]].valueChanged.connect(self.update_score)

            self.proxy_spinscore = self.scene.addWidget(self.spin_score[list_j[x][0]])

            width_score = self.proxy_spinscore.size().width()
            height_score = self.proxy_spinscore.size().height()

            self.proxy_spinscore.setPos(
                int(self.w_s / 2 - r * 2) + coord_score[f"{x}"][0] - width_score / 2,
                int(self.h_s / 2 - r) + coord_score[f"{x}"][1] - height_score / 2)

            if os.path.isfile(os.path.join(CONFIG_DIR, list_players_db()[list_j[x][0]]["avatar"])):
                avatar = Image.open(os.path.join(CONFIG_DIR, list_players_db()[list_j[x][0]]["avatar"]))
                avatar = avatar.resize((int(self.w_s / 20), int(self.w_s / 20)))
                avatar_Qt = QPixmap.fromImage(ImageQt.ImageQt(avatar))
            else:
                im.append(QPixmap(int(self.w_s / 20), int(self.w_s / 20)))
                im[-1].fill(QColor(0, 0, 0, 1))
                p = QPainter(im[-1])
                p.setRenderHints(QPainter.Antialiasing)
                p.setPen(QPen(QColor("#80135b")))
                p.setBrush(QBrush(QColor("#80135b")))
                p.drawEllipse(0, 0, int(self.w_s / 20), int(self.w_s / 20))
                p.end()
                avatar_Qt = im[-1]

            self.avatar = QGraphicsPixmapItem(avatar_Qt)

            gap_y = 0
            if x > 5:
                gap_y = metrics1.height()

            self.avatar.setPos(int(self.w_s / 2 - r * 2) + coord_avatar[f"{x}"][0] - avatar_Qt.width() / 2,
                               int(self.h_s / 2 - r) + coord_avatar[f"{x}"][1] - avatar_Qt.height() / 2 - gap_y)
            self.scene.addItem(self.avatar)

            self.name = QGraphicsTextItem(f"{list_j[x][1]}")
            self.name.setFont(font1)
            self.name.setDefaultTextColor(QColor("#ffffff"))
            self.name.setPos(int(self.w_s / 2 - r * 2) + coord_avatar[f"{x}"][0]
                             - metrics1.boundingRect(f"{list_j[x][1]}").width() / 2,
                             int(self.h_s / 2 - r) + coord_avatar[f"{x}"][1] + avatar_Qt.height() / 2
                             - metrics1.height() / 10 - gap_y)
            self.scene.addItem(self.name)

        self.btn_valid = QPushButton(" Valider ")
        self.btn_valid.setObjectName("validscore")
        self.btn_valid.clicked.connect(self.valid_score)
        self.proxy_btnvalid = self.scene.addWidget(self.btn_valid)
        width_btn = self.proxy_btnvalid.size().width()
        height_btn = self.proxy_btnvalid.size().height()
        self.proxy_btnvalid.setPos(
            int(self.w_s / 2) - width_btn / 2,
            int(self.h_s / 2) + height_btn)

        self.display_chips = QGraphicsTextItem()
        self.display_chips.setFont(self.font2)
        self.display_chips.setDefaultTextColor(QColor("#ffffff"))
        self.scene.addItem(self.display_chips)
        self.update_score()

    def update_score(self):

        sum_chip = 0
        for x in self.spin_score.keys():
            sum_chip += self.spin_score[x].value()
        self.display_chips.setPos(
            int(self.w_s / 2) - self.metrics2.boundingRect(f"{sum_chip} / {self.chip_max}").width() / 2,
            int(self.h_s / 2) - self.metrics2.height() / 2)
        self.display_chips.setPlainText(f"{sum_chip} / {self.chip_max}")

        self.proxy_btnvalid.setVisible(False)
        if sum_chip == self.chip_max:
            self.proxy_btnvalid.setVisible(True)

    def valid_score(self):
        for key in self.spin_score.keys():
            save_result_db(self.spin_score[key].value(), key, self.id_game)
        self.window_result = results.MainWindow(id_game=self.id_game)
        self.window_result.setWindowModality(Qt.ApplicationModal)
        self.window_result.showMaximized()
        self.destroy()

    def keyPressEvent(self, event: QKeyEvent) -> None:

        if self.game_progress and event.key() == 32:

            if not self.timer.isActive():
                self.logo_pause.setVisible(False)
                self.timer.start(self.time_step, self)

            elif self.timer.isActive():
                self.logo_pause.setVisible(True)
                self.timer.stop()

    class CaveAvatar(QGraphicsPixmapItem):

        def __init__(self, pixmap, id_player, id_game, text_nbcave):
            super().__init__(pixmap)
            self.id_player = id_player
            self.id_game = id_game
            self.text_nbcave = text_nbcave
            self.setCursor(QCursor(Qt.PointingHandCursor))

        def mouseDoubleClickEvent(self, e):
            msgBoxConfirm = QMessageBox()
            msgBoxConfirm.setWindowFlags(Qt.FramelessWindowHint)
            msgBoxConfirm.setIcon(QMessageBox.Icon.Question)
            msgBoxConfirm.setInformativeText(
                f"<br>"
                f"<b>{self.id_player[1]}</b> paye {cave_info(self.id_game)[2]} €<br>"
                f"pour une {self.id_player[3] + 2}<sup>ème</sup> cave de {cave_info(self.id_game)[1]} jetons ?<br>")
            addCave = msgBoxConfirm.addButton("Oui", QMessageBox.YesRole)
            addCave.setMinimumWidth(250)
            msgBoxConfirm.addButton("Non", QMessageBox.RejectRole)
            msgBoxConfirm.exec()
            if msgBoxConfirm.clickedButton() == addCave:
                self.id_player = (self.id_player[0], self.id_player[1], self.id_player[2], self.id_player[3] + 1)
                save_add_cave(self.id_player[3], self.id_player[0], self.id_game)
                self.text_nbcave.setPlainText("'" * (self.id_player[3] + 1))


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()

    with open("../../dark_blue.qss", "r") as file:
        _style = file.read()
        app.setStyleSheet(_style)
    ecran = app.screens()[0]
    win = ChronoWindow(15, 1920, 1080)
    win.showMaximized()
    app.exec()
