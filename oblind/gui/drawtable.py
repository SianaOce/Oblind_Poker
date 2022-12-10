from PySide6.QtWidgets import QGraphicsItem, QApplication, QGraphicsView
from PySide6.QtGui import QPen, QBrush, QColor, Qt, QFont, QFontMetrics, QPainter
from PySide6.QtCore import QRectF
from math import pi, cos, sin


class Table(QGraphicsItem):

    def __init__(self, w, p_r):
        super().__init__()
        self.w_t = p_r * w
        self.h_t = self.w_t / 2
        self.r = self.h_t / 2
        self.pos_line = w / 14
        self.x = int(w / 2 - self.w_t / 2)
        self.y = int(w / 4 - self.h_t / 2) 


    def boundingRect(self):
        pen_width = 20
        return QRectF(self.x - pen_width / 2, self.y - pen_width / 2, self.w_t + pen_width, self.h_t + pen_width)

    def paint(self, painter, option, widget):
        round_table = QPen()
        round_table.setWidth(20)
        round_table.setColor(QColor("#0d0f0d"))
        mark_table = QPen()
        mark_table.setWidth(2)
        mark_table.setColor("#bac2bc")

        painter.setBrush(QBrush(QColor("#074a10")))
        painter.setPen(round_table)
        painter.drawRoundedRect(self.x, self.y, self.w_t, self.h_t, self.r, self.r)

        painter.setBrush(QBrush(Qt.NoBrush))
        painter.setPen(QPen(mark_table))

        painter.drawRoundedRect(self.x + self.pos_line, self.y + self.pos_line, self.w_t - self.pos_line * 2,
                                self.h_t - self.pos_line * 2,
                                self.h_t / 2 - self.pos_line, self.h_t / 2 - self.pos_line)

        painter.setPen(QColor("#9c0505"))
        painter.setBrush(QBrush(QColor("#e00000")))
        red_mark = calc_coord(self.r, self.r, 6)
        for x in range(10):
            painter.drawEllipse(self.x + red_mark[f"{x}"][0], self.y + red_mark[f"{x}"][1], 6, 6)


def calc_coord(r1, r2, pen):
    # pour une table ovale avec hauteur = largeur/2 et rayon = largeur/2
    # r2 => rayon de la table
    # r1 => rayon des elements à placer
    # pen => largeur du crayon
    # => retourne 10 coordonnees autour de la table

    l_coord = {}
    if pen:
        pen = pen / 2

    # 4 positions sur cercle gauche

    l_coord["1"] = ([r2 - pen + int(r1 * cos(3 * pi / 2)), r2 - pen + int(r1 * sin(3 * pi / 2))])
    l_coord["0"] = ([r2 - pen + int(r1 * cos(pi + pi / 6)), r2 - pen + int(r1 * sin(pi + pi / 6))])
    l_coord["9"] = ([r2 - pen + int(r1 * cos(pi - pi / 6)), r2 - pen + int(r1 * sin(pi - pi / 6))])
    l_coord["8"] = ([r2 - pen + int(r1 * cos(pi / 2)), r2 - pen + int(r1 * sin(pi / 2))])

    # 2 positions sur cercle central
    l_coord["2"] = ([2 * r2 - pen + int(r1 * cos(3 * pi / 2)), r2 - pen + int(r1 * sin(3 * pi / 2))])
    l_coord["7"] = ([2 * r2 - pen + int(r1 * cos(pi / 2)), r2 - pen + int(r1 * sin(pi / 2))])
    # 4 positions sur cercle gauche
    l_coord["3"] = ([3 * r2 - pen + int(r1 * cos(3 * pi / 2)), r2 - pen + int(r1 * sin(3 * pi / 2))])
    l_coord["5"] = ([3 * r2 - pen + int(r1 * cos(pi / 6)), r2 - pen + int(r1 * sin(pi / 6))])
    l_coord["4"] = ([3 * r2 - pen + int(r1 * cos(2 * pi - pi / 6)), r2 - pen + int(r1 * sin(2 * pi - pi / 6))])
    l_coord["6"] = ([3 * r2 - pen + int(r1 * cos(pi / 2)), r2 - pen + int(r1 * sin(pi / 2))])

    return l_coord
