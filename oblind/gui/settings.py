import os
import random
from datetime import date

from PIL import Image
from PySide6.QtWidgets import QWidget, QTabWidget, QListWidget, QLineEdit, QPushButton, QSpinBox, QLabel, \
    QHBoxLayout, QGridLayout, QFormLayout, QListWidgetItem, QMessageBox, QDialog, QFileDialog, QInputDialog
from PySide6.QtGui import Qt, QPixmap, QMouseEvent, QCloseEvent

from oblind.constants import CONFIG_DIR
from oblind.bdsql import list_players_db, add_player_db, modify_player_db, delete_player_db
from oblind.chips import list_chips, create_chip, delete_chip, chip_maj_qty, verify_name

from oblind.gui import createavatar


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration")
        self.setMinimumHeight(500)
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.configs_tab = QTabWidget()
        self.widget_players_tab = QWidget()
        self.widget_chips_tab = QWidget()
        self.list_player = QListWidget()
        self.text_name = QLineEdit()
        self.text_firstname = QLineEdit()
        self.text_create_date = QLineEdit()
        self.text_avatar = QLineEdit()
        self.label_avatar = QLabel()
        self.loadavatar_btn = QPushButton("Charger image avatar...")
        self.createavatar_btn = QPushButton("Créer image avatar...")

        self.btn_add_player = QPushButton("Ajouter...")
        self.btn_del_player = QPushButton("Supprimer...")

        self.list_chips = QListWidget()
        self.label_visualchip = LabelClick(self)
        self.text_chipname = QLineEdit()
        self.value_chip = QSpinBox()
        self.qty_chip = QSpinBox()
        self.chip_use = QLineEdit()
        self.chip_nbuse = QLineEdit()
        self.btn_add_chip = QPushButton("+")
        self.btn_del_chip = QPushButton("-")

    def modify_widgets(self):
        self.configs_tab.addTab(self.widget_players_tab, "Joueurs")
        self.configs_tab.addTab(self.widget_chips_tab, "Jetons")
        self.text_avatar.setEnabled(False)
        self.text_create_date.setEnabled(False)
        self.value_chip.setRange(1, 10000)
        self.qty_chip.setRange(1, 1000)
        self.list_chips.setMinimumHeight(400)
        self.text_chipname.setReadOnly(True)
        self.btn_add_chip.setMinimumWidth(160)
        self.btn_del_chip.setMinimumWidth(160)
        self.update_listplayer()
        self.update_listjeton()

    def create_layouts(self):
        self.layout_config_window = QHBoxLayout(self)
        self.layout_players_tab = QGridLayout(self.widget_players_tab)
        self.layout_form_player = QFormLayout()
        self.layout_chips_tab = QGridLayout(self.widget_chips_tab)
        self.layout_form_chip = QFormLayout()

    def add_widgets_to_layouts(self):
        self.layout_config_window.addWidget(self.configs_tab)
        self.layout_players_tab.addWidget(self.list_player, 1, 1, 3, 1)
        self.layout_players_tab.addWidget(self.label_avatar, 1, 2, 1, 1, alignment=Qt.AlignCenter)
        self.layout_players_tab.addWidget(self.loadavatar_btn, 2, 2, 1, 1)
        self.layout_players_tab.addWidget(self.createavatar_btn, 3, 2, 1, 1)
        self.layout_players_tab.addLayout(self.layout_form_player, 4, 2, 1, 1)
        self.layout_form_player.addRow("Nom", self.text_name)
        self.layout_form_player.addRow("Prénom", self.text_firstname)
        self.layout_form_player.addRow("Avatar", self.text_avatar)
        self.layout_form_player.addRow("Date de création", self.text_create_date)
        self.layout_players_tab.addWidget(self.btn_add_player, 4, 1, 1, 1)
        self.layout_players_tab.addWidget(self.btn_del_player, 5, 1, 1, 1)

        self.layout_chips_tab.addWidget(self.list_chips, 1, 1, 2, 2)
        self.layout_chips_tab.addWidget(self.btn_add_chip, 1, 3, 1, 1)
        self.layout_chips_tab.addWidget(self.btn_del_chip, 3, 3, 1, 1)
        self.layout_chips_tab.addWidget(self.label_visualchip, 2, 3, 1, 1)
        self.layout_form_chip.addRow("Nom", self.text_chipname)
        self.layout_form_chip.addRow("Valeur", self.value_chip)
        self.layout_form_chip.addRow("Quantité", self.qty_chip)
        self.layout_form_chip.addRow("Utilisé", self.chip_use)
        self.layout_form_chip.addRow("Nombre par cave", self.chip_nbuse)
        self.layout_chips_tab.addLayout(self.layout_form_chip, 4, 2, 1, 1)

        self.layout_chips_tab.setVerticalSpacing(20)
        self.layout_chips_tab.setHorizontalSpacing(20)

    def setup_connections(self):
        self.btn_add_player.clicked.connect(self.add_player)
        self.list_player.currentItemChanged.connect(self.select_player)
        self.btn_del_player.clicked.connect(self.del_player)
        self.loadavatar_btn.clicked.connect(self.load_avatar)
        self.createavatar_btn.clicked.connect(self.create_avatar)

        self.list_chips.currentItemChanged.connect(self.select_chip)
        self.btn_add_chip.clicked.connect(self.add_chip)
        self.btn_del_chip.clicked.connect(self.del_chip)

    def add_player(self):
        ind = self.list_player.currentIndex().data(Qt.UserRole)
        self.verif_modif(ind)
        add_player_db(name="Nom", lastname="Prenom", date=date.today(), avatar="")
        self.list_player.setCurrentRow(-1)
        self.update_listplayer()
        self.list_player.setCurrentRow(self.list_player.count() - 1)

    def del_player(self):
        # Récuperation de l'id du joueur selectionné
        delete_player_db(self.list_player.currentIndex().data(Qt.UserRole))
        self.update_listplayer()

    def select_player(self, cur, prev):
        # Récuperation n° ligne selectionnée et id player correspondant
        row_sel = self.list_player.currentRow()
        cur_ind = self.list_player.currentIndex().data(Qt.UserRole)

        # si selection actuelle non nulle (clear lors de update_list)
        if row_sel != -1:
            # si existence d'une selection anterieure
            if isinstance(prev, QListWidgetItem):

                # Récuperation de l'id player precedement selectionné
                pre_ind = prev.data(Qt.UserRole)

                # Vérification si des modifications ont été effectuées
                if (self.text_name.text(), self.text_firstname.text(), self.text_avatar.text()) != (
                        self.db[pre_ind]["name"], self.db[pre_ind]["lastname"], self.db[pre_ind]["avatar"]):
                    save_dialog_box = QMessageBox(self)
                    save_dialog_box.setText(f"Sauvegarder les changements pour {prev.text()}")
                    save_dialog_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save)
                    # Sauvegarde des modifications
                    if save_dialog_box.exec_() == QMessageBox.Save:
                        modify_player_db(self.text_name.text(), self.text_firstname.text(), self.text_avatar.text(),
                                         pre_ind)
                        self.update_listplayer()
                        self.list_player.setCurrentRow(row_sel)

            # Chargement des informations du joueur selectionné

            self.text_name.setText(self.db[cur_ind]["name"])
            self.text_firstname.setText(self.db[cur_ind]["lastname"])
            self.text_create_date.setText(self.db[cur_ind]["date_create"])
            self.text_avatar.setText(self.db[cur_ind]["avatar"])
            self.image_avatar = os.path.join(CONFIG_DIR, self.db[cur_ind]["avatar"])
            self.label_avatar.setPixmap(QPixmap(self.image_avatar))

    def update_listplayer(self):

        self.list_player.clear()
        self.db = list_players_db()

        for i in self.db:
            item = QListWidgetItem(f"#{i}# - {self.db[i]['lastname']} {self.db[i]['name']}")
            item.setData(Qt.UserRole, i)
            self.list_player.addItem(item)

    def load_avatar(self):
        file_dialog = QFileDialog(self)
        file_dialog.setMimeTypeFilters(["image/png"])
        if file_dialog.exec_() == QDialog.Accepted:
            source_path = file_dialog.selectedFiles()[0]
            self.save_avatar(source_path)

    def create_avatar(self):
        self.createa = createavatar.CreateAvatar()
        self.createa.exec()
        self.save_avatar(self.createa.image_created)

    def save_avatar(self, source_path):
        im = Image.open(source_path)
        text_avatar = f"{self.list_player.currentIndex().row() + 1}_{random.randint(00000, 99999)}.png"
        im.save(os.path.join(CONFIG_DIR, text_avatar))
        self.text_avatar.setText(text_avatar)
        self.image_avatar = os.path.join(CONFIG_DIR, text_avatar)
        self.label_avatar.setPixmap(QPixmap(self.image_avatar))


    def update_listjeton(self):
        self.jetons = list_chips()
        self.list_chips.clear()
        for key, item in self.jetons.items():
            self.list_chips.addItem(key)

    def select_chip(self, curr, prev):
        cur_ind = self.list_chips.currentRow()

        if isinstance(prev, QListWidgetItem) and cur_ind != -1:
            chip_maj_qty(prev.text(), self.qty_chip.value())
            self.update_listjeton()
            self.list_chips.setCurrentRow(cur_ind)

        if self.list_chips.currentItem():
            self.text_chipname.setText(self.list_chips.currentItem().text())
            self.value_chip.setValue(self.jetons[self.list_chips.currentItem().text()]["value"])
            self.qty_chip.setValue(self.jetons[self.list_chips.currentItem().text()]["qty_total"])

            if os.path.exists(os.path.join(CONFIG_DIR, f"{self.list_chips.currentItem().text()}.png")):
                self.image_chip = os.path.join(CONFIG_DIR, f"{self.list_chips.currentItem().text()}.png")
            else:
                self.image_chip = "resources/chip.png"

            self.label_visualchip.setPixmap(QPixmap(self.image_chip))

    def add_chip(self):
        text, ok = QInputDialog().getText(self, "Nouveau jeton", "Saisir un nom:", QLineEdit.Normal)
        if ok and text and verify_name(text):
            create_chip(text, 0)
            self.update_listjeton()
            self.list_chips.setCurrentRow(self.list_chips.count() - 1)

    def del_chip(self):
        if self.list_chips.currentRow() != -1:
            delete_chip(self.list_chips.currentItem().text())
            self.update_listjeton()

    def load_chipimage(self):
        file_dialog = QFileDialog(self)
        file_dialog.setMimeTypeFilters(["image/png"])
        if file_dialog.exec_() == QDialog.Accepted:
            chemin_acces = file_dialog.selectedFiles()[0]
            im = Image.open(chemin_acces)
            image_150 = im.resize((150, 150))
            text_chip = f"{self.text_chipname.text()}.png"
            image_150.save(os.path.join(CONFIG_DIR, text_chip))
            self.image_chip = os.path.join(CONFIG_DIR, text_chip)
            self.label_visualchip.setPixmap(QPixmap(self.image_chip))

    def verif_modif(self, ind):
        # Vérification si des modifications ont été effectuées
        if ind and (self.text_name.text(), self.text_firstname.text(), self.text_avatar.text()) != (
                self.db[ind]["name"], self.db[ind]["lastname"], self.db[ind]["avatar"]):
            save_dialog_box = QMessageBox(self)
            save_dialog_box.setText(f"Sauvegarder les changements pour :\n\n{self.list_player.currentItem().text()}\n")
            save_dialog_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save)
            # Sauvegarde des modifications
            if save_dialog_box.exec_() == QMessageBox.Save:
                modify_player_db(self.text_name.text(), self.text_firstname.text(), self.text_avatar.text(), ind)

    def closeEvent(self, event: QCloseEvent) -> None:

        ind = self.list_player.currentIndex().data(Qt.UserRole)
        self.verif_modif(ind)


class LabelClick(QLabel):

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.parent = parent

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.parent.load_chipimage()
