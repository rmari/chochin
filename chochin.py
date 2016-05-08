#!/usr/bin/env python

#    Copyright 2016 Romain Mari
#    This file is part of Chochin.
#
#    Chochin is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# PyQt4 imports
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore

import chochinCanvas as cCanvas


class SceneInfoWidget(QtGui.QWidget):
    def __init__(self, parent, width, height):
        super(SceneInfoWidget, self).__init__(parent=parent)

        self.setGeometry(0, 0, width, height)

        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)
        # pal = QtGui.QPalette()
        # self.setBackgroundRole(QtGui.QPalette.Window)
        # pal.setColor(self.backgroundRole(),
                    #  QtGui.QColor(200, 0, 0, 0))
                    # self.setAutoFillBackground(True)
        # self.setPalette(pal)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.show()
def paintEvent(self, event):

    painter = QPainter()
    painter.begin(self)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
    painter.setPen(QPen(Qt.NoPen))
    self.counter = 0
    for i in range(6):
        if (self.counter / 5) % 6 == i:
            painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
    else:
        painter.setBrush(QBrush(QColor(127, 127, 127)))
        painter.drawEllipse(
         self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) -                  self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) -                  20, 20)

    painter.end()
    # def paintEvent(self, event):
    #     backgroundColor = QtGui.QColor(200, 0, 0, 0)
    #     backgroundColor.setAlpha(200)
    #     customPainter = QtGui.QPainter(self)
    #     customPainter.fillRect(self.rect(),backgroundColor)

if __name__ == '__main__':
    import sys

    class ChochinWindow(QtGui.QMainWindow):
        verbosity = True

        def __init__(self, filename):
            super(ChochinWindow, self).__init__()

            # initialize the GL widget
            self.datawidget = cCanvas.ChochinCanvas()
            self.setGeometry(100,
                             100,
                             self.datawidget.width,
                             self.datawidget.height)
            self.setCentralWidget(self.datawidget)

            self.scene_info_widget = SceneInfoWidget(self, 100, 100)
            self.show()
            self.datawidget.setFile(filename)

        def keyPressEvent(self, event):
            e = event.key()
            if e == QtCore.Qt.Key_Q:
                self.close()
            elif e == QtCore.Qt.Key_V:
                self.verbosity = not self.verbosity
            else:
                self.datawidget.keyPressEvent(event)
            self.scene_info_widget.update()
    app = QtGui.QApplication(sys.argv)
    window = ChochinWindow(sys.argv[1])
    window.show()
    app.exec_()
