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
from PyQt4.QtCore import Qt
from PyQt4 import QtGui, QtCore

import chochinCanvas as cCanvas


class SceneInfoWidget(QtGui.QWidget):
    frame_info_box = QtCore.QRectF(15, 10, 120, 18)
    layer_info_boxes = [QtCore.QRectF(a, b, 20, 20)
                        for a, b in zip(range(15, 150, 25), ([50]*6))]
    layer_info_boxes += [QtCore.QRectF(a, b, 20, 20)
                         for a, b in zip(range(15, 150, 25), ([75]*6))]
    font = QtGui.QFont()
    font.setPixelSize(12)

    def __init__(self, parent, width, height):
        super(SceneInfoWidget, self).__init__(parent=parent)

        self.setGeometry(0, 0, width, height)

        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtGui.QColor(100, 100, 100))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.show()

    def setFrame(self, frame):
        self.frame = frame

    def setLayers(self, layers):
        self.layers = layers

    def drawActiveLayer(self, painter, rect, layer_nb):
        bgcolor = QtCore.Qt.white
        painter.setPen(bgcolor)
        painter.setBrush(bgcolor)
        painter.drawRoundedRect(rect, 20, 20, mode=Qt.RelativeSize)

        textcolor = QtCore.Qt.black
        painter.setPen(textcolor)

        painter.drawText(rect, QtCore.Qt.AlignCenter, str(layer_nb))

    def drawInactiveLayer(self, painter, rect, layer_nb):
        textcolor = QtCore.Qt.black
        painter.setPen(textcolor)

        painter.drawText(rect, QtCore.Qt.AlignCenter, str(layer_nb))

    def paintEvent(self, event):

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.setFont(self.font)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(QtCore.Qt.white)
        painter.drawText(self.frame_info_box, QtCore.Qt.AlignLeft,
                         "Frame "+str(self.frame+1)+" (n p)")

        painter.drawText(self.frame_info_box, QtCore.Qt.AlignLeft,
                         "Frame "+str(self.frame+1)+" (n p)")
        for i in range(len(self.layers)):
            if self.layers[i]:
                self.drawActiveLayer(painter, self.layer_info_boxes[i], i+1)
            else:
                self.drawInactiveLayer(painter, self.layer_info_boxes[i], i+1)

        painter.end()

if __name__ == '__main__':
    import sys

    class ChochinWindow(QtGui.QMainWindow):
        verbosity = True
        timer = QtCore.QBasicTimer()

        def __init__(self, filename):
            super(ChochinWindow, self).__init__()

            # initialize the GL widget
            self.datawidget = cCanvas.ChochinCanvas()
            self.setGeometry(100,
                             100,
                             self.datawidget.width,
                             self.datawidget.height)
            self.setWindowTitle("Chōchin - " + filename)
            self.setCentralWidget(self.datawidget)

            self.scene_info_widget = SceneInfoWidget(self, 180, 120)
            self.show()

            self.datawidget.setFile(filename)
            self.setInfoWidget()

        def setInfoWidget(self):
            layers = self.datawidget.layer_activity
            self.scene_info_widget.setLayers(layers)
            self.scene_info_widget.setFrame(self.datawidget.frame)

        def keyPressEvent(self, event):
            e = event.key()
            if e == QtCore.Qt.Key_Q:
                self.datawidget.close()
                self.close()
            elif e == QtCore.Qt.Key_V:
                self.verbosity = not self.verbosity
                if self.verbosity:
                    self.scene_info_widget.show()
                else:
                    self.scene_info_widget.hide()
            else:
                self.datawidget.keyPressEvent(event)

            if self.verbosity:
                self.setInfoWidget()
                self.scene_info_widget.update()

        def timerEvent(self, event):
            self.datawidget.timerEvent(event)

            if self.verbosity:
                self.setInfoWidget()
                self.scene_info_widget.update()

    if len(sys.argv) < 2:
        print("Usage:\n chochin.py input_file")
        exit(1)
    app = QtGui.QApplication(sys.argv)
    window = ChochinWindow(sys.argv[1])
    window.show()
    app.exec_()
