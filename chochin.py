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

if __name__ == '__main__':
    import sys

    class ChochinWindow(QtGui.QMainWindow):
        verbosity = True

        def __init__(self, filename):
            super(ChochinWindow, self).__init__()

            # initialize the GL widget
            self.widget = cCanvas.ChochinCanvas()
            # put the window at the screen position (100, 100)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()
            self.widget.setFile(filename)

        def keyPressEvent(self, event):
            e = event.key()
            if e == QtCore.Qt.Key_Q:
                self.close()
            elif e == QtCore.Qt.Key_V:
                self.verbosity = not self.verbosity
            else:
                self.widget.keyPressEvent(event)
            self.update()
    # create the Qt App and window
    app = QtGui.QApplication(sys.argv)
    window = ChochinWindow(sys.argv[1])
    window.show()
    app.exec_()
