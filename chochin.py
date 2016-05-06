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
from PyQt4 import QtGui, QtCore

import chochinCanvas as cCanvas


class SceneInfoWidget(QtGui.QWidget):
    def __init__(self, parent, width, height):
        super(SceneInfoWidget, self).__init__(parent=parent)

        self.setGeometry(0, 0, width, height)

        pal = self.palette()
        pal.setColor(self.backgroundRole(),
                     QtGui.QColor(200, 0, 0, 255))
        self.setAutoFillBackground(True)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, 50)
        self.show()

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

    app = QtGui.QApplication(sys.argv)
    window = ChochinWindow(sys.argv[1])
    window.show()
    app.exec_()
