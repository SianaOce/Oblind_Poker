from PySide6.QtWidgets import QWidget, QListWidget, QLabel, QListWidgetItem, QAbstractItemView, QGridLayout, \
    QSpacerItem, QSizePolicy
from PySide6.QtGui import QFont, QColor, Qt, QPainter
from PySide6.QtCharts import QChart, QPieSeries, QPieSlice, QChartView

from oblind.bdsql import list_players_game, cave_info, list_game

font_1 = QFont("DejaVu Sans Condensed", 12)
font_2 = QFont("DejaVu Sans Condensed", 10)
font_3 = QFont("DejaVu Sans Condensed", 8)


class ResultPie(QChart):

    def __init__(self, result_game, info_game):
        super().__init__()

        self.result_game = result_game
        self.info_game = info_game

        nb = len(result_game)
        score = [(i[2] / info_game[1]) * info_game[2] for i in result_game]
        result_legend = [str(i[2]) + " - " + i[1] for i in result_game]
        legend_names = [f"<u>{i[1]}</u> - {i[2]}<br>{round((i[2] / info_game[1]) * info_game[2], 2)} €" for i in
                        result_game]

        self.trecave = "sans"
        if info_game[4]:
            self.trecave = "avec"
            legend_names = [f"<u>{i[1]}</u> - {i[2]}<br>{round((i[2] / info_game[1]) * info_game[2], 2)} €" \
                            f" <i>({round((1 + i[3]) * info_game[2], 2)} €)</i>" for i in result_game]

        self.titre_pie = f"<u>Partie {info_game[3]} du {info_game[0]} {self.trecave} recave</u> | " \
                         f"<i>{info_game[1]} jetons {info_game[2]} €</i>"

        self.series1 = QPieSeries()
        self.setTheme(QChart.ChartThemeBlueCerulean)

        for i in range(nb):
            self.series1.append(result_legend[i], score[i])

            if score[i] != 0:
                self.slices1 = self.series1.slices()[i]
                self.slices1.setLabelPosition(QPieSlice.LabelOutside)
                self.slices1.setLabelArmLengthFactor(0.25)
                self.slices1.setLabelColor(QColor("#f2fff5"))
                self.slices1.setLabelFont(font_3)
                self.slices1.setLabelVisible(True)
                if i == 0:
                    self.slices1.setExploded(True)

        self.setTitle(self.titre_pie)
        self.setTitleFont(font_1)
        self.addSeries(self.series1)
        self.legend().setVisible(True)
        self.legend().setFont(font_2)
        self.legend().setAlignment(Qt.AlignRight)
        self.setAnimationOptions(QChart.SeriesAnimations)

        for series in self.series():
            markers = self.legend().markers(series)
            n = 0
            for marker in markers:
                marker.setLabel(legend_names[n])
                n += 1


class MainWindow(QWidget):

    def __init__(self, id_game):
        super().__init__()
        self.id_game = id_game
        self.games_max = 4
        self.setWindowTitle("Résultats")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setup_ui()
        self.pie = []
        if id_game:
            self.build_pie([id_game])

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.list_game = QListWidget()
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gain_tot = QLabel("")
        self.spacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def modify_widgets(self):

        for x in list_game():
            item = QListWidgetItem(f"{x[0]} - {x[1]}")
            item.setData(Qt.UserRole, x[0])
            self.list_game.addItem(item)

        self.list_game.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_game.setMinimumWidth(210)
        self.list_game.setMaximumWidth(300)
        self.list_game.setMinimumHeight(500)
        self.list_game.setStyleSheet("font-size: 16px")
        self.gain_tot.setAlignment(Qt.AlignRight)
        self.gain_tot.setObjectName("lbl_result")

    def create_layouts(self):
        self.main_layout = QGridLayout(self)
        self.pies_layout = QGridLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.list_game, 0, 0)
        self.main_layout.addItem(self.spacer, 1, 0)
        self.main_layout.addWidget(self.gain_tot, 2, 0)
        self.main_layout.addItem(self.spacer2, 3, 0)
        self.main_layout.addLayout(self.pies_layout, 0, 1, 4, 2)

    def setup_connections(self):
        self.list_game.itemClicked.connect(self.choice_game)

    def choice_game(self):
        if len(self.list_game.selectedItems()) > self.games_max:
            self.list_game.currentItem().setSelected(False)

        l_g = []
        for x in self.list_game.selectedItems():
            l_g.append(x.data(Qt.UserRole))

        self.build_pie(l_g)

    def build_pie(self, l_g):

        # supprimer l'ensemble des graphiques
        if self.pie:
            for w in self.pie:
                self.pie.remove(w)
                self.pies_layout.removeWidget(w)
                w.deleteLater()

        for x in range(len(l_g)):
            self.pie.append(QChartView())
            self.pie[x].setRenderHint(QPainter.Antialiasing)
            if x < 2:
                self.pies_layout.addWidget(self.pie[x], 0, x)
            else:
                self.pies_layout.addWidget(self.pie[x], 1, x - 2)

        if l_g:

            z = 0
            sum_game = {}
            for id_game in l_g:
                result_game = list_players_game(id_game)
                info_game = cave_info(id_game)
                for game in result_game:
                    gain = (game[2] / info_game[1]) * info_game[2]
                    sum_game[game[1]] = round(sum_game.get(game[1], 0) + gain, 2)

                sort_gain = sorted(sum_game.items(), key=lambda t: t[1], reverse=True)
                l_text = "<br>"
                for txt in sort_gain:
                    l_text = l_text + f"{txt[0]} ►  {txt[1]:.2f} €<br>"
                self.gain_tot.setText(l_text)

                pie = ResultPie(result_game, info_game)
                self.pie[z].setChart(pie)
                self.pie[z].setVisible(True)
                z += 1
        else:
            self.gain_tot.setText("-")
