#    Copyright 2014 Romain Mari
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

import sys
import os
import numpy as np

# PyQt5 imports
from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets
from PyQt5.QtOpenGL import QGLWidget

# PyOpenGL imports
import OpenGL.GL as gl
import chochinPrimitives as cPrim
import chochinFile as cFile
import chochinScene as cScene

color_fname = "chochin_palette.py"
if os.path.isfile(color_fname):
    sys.path.append(".")
    import chochin_palette
    color_palette = chochin_palette.color_palette
else:
    color_palette = [QtCore.Qt.black,
                     (50, 50, 50, 255),
                     QtCore.Qt.white,
                     (255, 102, 102, 255),
                     (102, 0, 0, 255),
                     (0, 102, 0, 255),
                     (0, 0, 102, 255),
                     (255, 255, 102, 255),
                     (255, 152, 51, 255),
                     (102, 178, 255, 255),
                     (255, 153, 255, 255),
                     (0, 102, 102, 255),
                     (51, 102, 0, 255),
                     (51, 0, 102, 255),
                     (102, 0, 51, 255),
                     (102, 51, 0, 255),
                     (0, 51, 102, 255),
                     (32, 32, 32, 255),
                     (96, 96, 96, 255),
                     (192, 192, 192, 255)]

p = []
for c in color_palette:
    if isinstance(c, QtCore.Qt.GlobalColor):
        color = QtGui.QColor(c)
    else:
        color = QtGui.QColor(*c) # color as a tuple

    p.append(color.getRgbF())

color_palette = np.array(p)


class ChochinCanvas(QGLWidget):
    width, height = 600, 600
    speed = 10
    forward_anim = True
    frame = 0
    former_frame = 0
    init_offset = [0, 0]
    prefactor = ""

    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(
            self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
        self.installEventFilter(self)
        self.layer_activity = np.ones(12, dtype=bool)
        self.reality = 1

    def setSceneGeometry(self):
        self.scene.rotation = self.rotation
        self.scene.layer_list = self.layer_activity
        self.scene.scale = self.scale

    def setInitSceneGeometry(self):
        self.reset_rotation = np.zeros((3, 3))
        self.reset_rotation[0, 0] = 1
        self.reset_rotation[1, 2] = 1
        self.reset_rotation[2, 1] = 1
        self.rotation = self.reset_rotation[:]
        if self.scene.getLargestDimension() > 0:
            self.scale = 1./self.scene.getLargestDimension()
        else:
            self.scale = 1
        self.setSceneGeometry()

    def setFile(self, filename):
        print("[chochin] Set file")
        self.data = cFile.chochinFile(filename.encode("utf8"))

    def readFileAndDisplay(self):
        self.data.setPalette(color_palette)
        self.data.readChunk()
        print("[chochin] File loaded")
        self.scene = cScene.chochinScene(*self.data[self.frame])
        self.setInitSceneGeometry()
        self.loadScene()

    def loadScene(self):
        self.scene = cScene.chochinScene(*self.data[self.frame])
        self.setSceneGeometry()

        pos, attrs = self.scene.getDisplayedScene()
        # print(pos)
        self.object_types = []

        # sticks
        if "s" in pos:
            self.objects["s"].set_data(pos["s"],
                                       attrs["s"]["r"],
                                       attrs["s"]["@"],
                                       attrs["s"]["y"])
            self.object_types.append("s")

        # lines
        if "l" in pos:
            self.objects["l"].set_data(pos["l"],
                                       attrs["l"]["@"],
                                       attrs["l"]["y"])
            self.object_types.append("l")

        # circles
        if "c" in pos:
            self.objects["c"].set_data(pos["c"],
                                       attrs["c"]["r"],
                                       attrs["c"]["@"],
                                       attrs["c"]["y"])
            self.object_types.append("c")

        # texts
        if "t" in pos:
            self.objects["t"] = (pos["t"], attrs["t"])
            self.object_types.append("t")

    def setXRotation(self, angleX):
        sinAngleX = np.sin(angleX)
        cosAngleX = np.cos(angleX)
        generator = np.asmatrix([[1, 0, 0],
                            [0, cosAngleX, -sinAngleX],
                            [0, sinAngleX, cosAngleX]])
        self.rotation = generator*self.rotation

    def setYRotation(self, angleY):
        sinAngleY = np.sin(angleY)
        cosAngleY = np.cos(angleY)
        generator = np.asmatrix([[cosAngleY, -sinAngleY, 0],
                            [sinAngleY, cosAngleY, 0],
                            [0, 0, 1]])
        self.rotation = generator*self.rotation
        
    def start_anim(self):
        self.parent().timer.start(self.speed, self.parent())

    def goToFrame(self, n, loop=False):
        self.former_frame = self.frame
        frame_nb = self.data.frame_nb()
        if n > frame_nb - 2:
            if loop:
                self.frame = 0
            else:
                self.frame = frame_nb - 2
        elif n < 0:
            if loop:
                self.frame = frame_nb - 2
            else:
                self.frame = 0
        else:
            self.frame = n
        self.loadScene()

    def timerEvent(self, event):
        if event.timerId() == self.parent().timer.timerId():
            if self.forward_anim:
                self.goToFrame(self.frame + 1, loop=True)
            else:
                self.goToFrame(self.frame - 1, loop=True)
            self.update()
        else:
            QtGui.QWidget.timerEvent(self, event)

    def layerSwitch(self, label):
        self.layer_activity[label] = not self.layer_activity[label]

    def handleFrameSwitchKey(self, e, m):
        caught = False
        stop_anim = True
        if e == QtCore.Qt.Key_N and m != QtCore.Qt.ShiftModifier:
            try:
                inc_nb = int(self.prefactor)
                self.goToFrame(self.frame + inc_nb)
            except ValueError:
                self.goToFrame(self.frame + 1)
            caught = True
        elif e == QtCore.Qt.Key_P and m != QtCore.Qt.ShiftModifier:
            try:
                dec_nb = int(self.prefactor)
                self.goToFrame(self.frame - dec_nb)
            except ValueError:
                self.goToFrame(self.frame - 1)
            caught = True
        elif e == QtCore.Qt.Key_G and m != QtCore.Qt.ShiftModifier:
            try:
                f_nb = int(self.prefactor)-1
            except ValueError:
                f_nb = 0
            self.goToFrame(f_nb)
            caught = True
        elif e == QtCore.Qt.Key_Z:
            self.goToFrame(self.former_frame)
            caught = True
        elif e == QtCore.Qt.Key_N and m == QtCore.Qt.ShiftModifier:
            try:
                self.speed = int(1000./int(self.prefactor))  # timer in msec
            except ValueError:
                pass
            self.forward_anim = True
            self.start_anim()
            caught = True
            stop_anim = False
        elif e == QtCore.Qt.Key_P and m == QtCore.Qt.ShiftModifier:
            try:
                self.speed = int(1000./int(self.prefactor))  # timer in msec
            except ValueError:
                pass
            self.forward_anim = False
            self.start_anim()
            caught = True
            stop_anim = False
        elif e == QtCore.Qt.Key_G and m == QtCore.Qt.ShiftModifier:
            self.goToFrame(self.data.frame_nb() - 1)
            caught = True
        elif e == QtCore.Qt.Key_Space:
            caught = True

        if caught and stop_anim:
            if self.parent().timer.isActive():
                self.parent().timer.stop()

        return caught

    def handlePointOfViewKey(self, e, m):
        caught = False
        if e == QtCore.Qt.Key_Tab and m != QtCore.Qt.ShiftModifier:
            self.rotation = self.reset_rotation
            caught = True
        elif e == QtCore.Qt.Key_Tab and m == QtCore.Qt.ShiftModifier:
            self.offset = self.init_offset
            caught = True
        elif e == QtCore.Qt.Key_Asterisk:
            self.setPortSize(self.port_size*1.05)
            self.setViewPort()
            caught = True
        elif e == QtCore.Qt.Key_Slash:
            self.setPortSize(self.port_size/1.05)
            self.setViewPort()
            caught = True
        elif e == QtCore.Qt.Key_Up:
            if m != QtCore.Qt.ShiftModifier:
                try:
                    angleX = np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleX = 0.1
            else:
                angleX = 0.5*np.pi
            self.setXRotation(angleX)
            caught = True
        elif e == QtCore.Qt.Key_Down:
            if m != QtCore.Qt.ShiftModifier:
                try:
                    angleX = -np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleX = -0.1
            else:
                angleX = -0.5*np.pi
            self.setXRotation(angleX)
            caught = True
        elif e == QtCore.Qt.Key_Left:
            if m != QtCore.Qt.ShiftModifier:
                try:
                    angleY = np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleY = 0.1
            else:
                angleY = 0.5*np.pi
            self.setYRotation(angleY)
            caught = True
        elif e == QtCore.Qt.Key_Right:
            if m != QtCore.Qt.ShiftModifier:
                try:
                    angleY = -np.deg2rad(float(self.prefactor))
                except ValueError:
                    angleY = -0.1
            else:
                angleY = -0.5*np.pi
            self.setYRotation(angleY)
            caught = True

        if caught:
            self.loadScene()
        return caught

    def handleRealityKey(self, e, m):
        caught = False

        if e == QtCore.Qt.Key_Minus:
            self.reality = 0
            caught = True
        elif e == QtCore.Qt.Key_Plus:
            self.reality = 1
            caught = True
        return caught

    def handleLayerKey(self, e, m):
        caught = False

        if e == QtCore.Qt.Key_F1:
            self.layerSwitch(0)
            caught = True
        elif e == QtCore.Qt.Key_F2:
            self.layerSwitch(1)
            caught = True
        elif e == QtCore.Qt.Key_F3:
            self.layerSwitch(2)
            caught = True
        elif e == QtCore.Qt.Key_F4:
            self.layerSwitch(3)
            caught = True
        elif e == QtCore.Qt.Key_F5:
            self.layerSwitch(4)
            caught = True
        elif e == QtCore.Qt.Key_F6:
            self.layerSwitch(5)
            caught = True
        elif e == QtCore.Qt.Key_F7:
            self.layerSwitch(6)
            caught = True
        elif e == QtCore.Qt.Key_F8:
            self.layerSwitch(7)
            caught = True
        elif e == QtCore.Qt.Key_F9:
            self.layerSwitch(8)
            caught = True
        elif e == QtCore.Qt.Key_F10:
            self.layerSwitch(9)
            caught = True
        elif e == QtCore.Qt.Key_F11:
            self.layerSwitch(10)
            caught = True
        elif e == QtCore.Qt.Key_F12:
            self.layerSwitch(11)
            caught = True
        if caught:
            self.loadScene()
        return caught

    def handleKey(self, e, m):
        caught = self.handleLayerKey(e, m)
        if not caught:
            caught = self.handlePointOfViewKey(e, m)
        if not caught:
            caught = self.handleFrameSwitchKey(e, m)
        if not caught:
            caught = self.handleRealityKey(e, m)
        return caught

    def keyPressEvent(self, event):
        e = event.key()
        m = event.modifiers()
        if e == QtCore.Qt.Key_Return and self.old_e is not None:
            e, m, self.prefactor = self.old_e, self.old_m, self.old_prefactor
        self.old_prefactor = self.prefactor
        caught = self.handleKey(e, m)

        t = event.text()
        if e != QtCore.Qt.Key_Return:
            try:
                i = int(t)
                self.prefactor = self.prefactor + t
            except ValueError:
                if caught:
                    self.prefactor = ""

        if caught:
            self.old_e, self.old_m = e, m
            self.update()

    def mousePressEvent(self, event):
        modifier = QtWidgets.QApplication.keyboardModifiers()
        if event.button() == QtCore.Qt.LeftButton:
            self.current_point = event.pos()
            self.translate = False
            self.rotate = False
            if modifier == QtCore.Qt.ShiftModifier:
                self.translate = True
            else:
                self.rotate = True

    def mouseMoveEvent(self, event):
        self.previous_point = self.current_point
        self.current_point = event.pos()

        if self.translate:
            translateX = self.offset[0]\
                + (self.current_point.x() - self.previous_point.x())
            translateY = self.offset[1]\
                - (self.current_point.y() - self.previous_point.y())
            self.offset = [translateX, translateY]
            self.setViewPort()
        elif self.rotate:
            angleY = self.current_point.x() - self.previous_point.x()
            angleY *= -4/self.width
            self.setYRotation(angleY)

            angleX = self.current_point.y() - self.previous_point.y()
            angleX *= -4/self.height
            self.setXRotation(angleX)
            self.loadScene()

        self.update()

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        self.configureGL()
        self.objects = {}
        self.objects["s"] = cPrim.Sticks()
        self.objects["c"] = cPrim.Circles()
        self.objects["l"] = cPrim.Lines()

        self.setPortSize(min(self.width, self.height))
        self.offset = self.init_offset

    def writeTexts(self, painter):
        painter.setPen(QtCore.Qt.black)
        if "t" in self.object_types:
            pos, attrs = np.array(self.objects["t"][0]), self.objects["t"][1]
            pos = pos[:, :2]

            # go to gl "normalized device coordinates"
            pos *= self.scale
            # apply the transform from nd coords to viewport coords
            pos += 1
            pos *= 0.5*self.port_size
            pos += self.offset
            # now we need to account for the fact that in Qt y
            # is from top to bottom
            pos[:, 1] = self.height - pos[:, 1]

            for i in range(len(pos)):
                if self.layer_activity[attrs["y"][i]]:
                    color_array = np.array(attrs["@"][i])*255
                    color_array = color_array.astype(int)
                    painter.setPen(QtGui.QColor(*color_array))
                    painter.drawText(int(pos[i][0]),
                                     int(pos[i][1]),
                                     attrs["s"][i])

    def glpaint(self):
        # def paintGL(self): # if no paintEvent

        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        push_vector = [0, 0, self.scene.getLargestDimension()/2.]
        for t in ["s", "l"]:
            if t in self.object_types:
                self.objects[t].set_uniform('u_scale', self.scale)
                self.objects[t].set_uniform('u_push', push_vector)
                self.objects[t].set_uniform('u_active_layers',
                                            self.layer_activity)
                self.objects[t].draw()

        if "c" in self.object_types:
            self.objects["c"].set_uniform('u_scale', self.scale)
            self.objects["c"].set_uniform('u_rad_scale', self.rad_scale)
            self.objects["c"].set_uniform('u_linewidth', 1)
            self.objects["c"].set_uniform('u_antialias', 1)
            self.objects["c"].set_uniform('u_rotation',
                                          np.array(self.rotation,
                                                   dtype=np.float32))
            self.objects["c"].set_uniform('u_push', push_vector)
            self.objects["c"].set_uniform('u_active_layers',
                                          self.layer_activity)
            self.objects["c"].set_uniform('u_reality',
                                          self.reality)
            self.objects["c"].draw()

    def configureGL(self):
        gl.glClearColor(*color_palette[1])
        gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_MULTISAMPLE)
        gl.glEnable(gl.GL_POINT_SPRITE)
        
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def enableGLPainting(self, qpainter):
        qpainter.beginNativePainting()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        self.configureGL()
        self.setViewPort()
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        gl.glOrtho(-1, 1, 1, -1, -1, 1)

    def disableGLPainting(self, qpainter):
        gl.glDisable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)
        # gl.glDisable(gl.GL_MULTISAMPLE)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()
        qpainter.endNativePainting()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)

        self.enableGLPainting(p)
        self.glpaint()
        self.disableGLPainting(p)

        # p.begin(self)
        self.writeTexts(p)
        # p.end()

    def setPortSize(self, size):
        try:
            inflate = size/self.port_size
            self.offset[0] *= inflate
            self.offset[1] *= inflate

            self.offset[0] += self.width*(1-inflate)/2
            self.offset[1] += self.height*(1-inflate)/2
            self.offset[0] = int(self.offset[0])
            self.offset[1] = int(self.offset[1])
        except AttributeError:   # for init time
            pass

        self.port_size = int(size)
        self.rad_scale = self.port_size

    def setViewPort(self):
        gl.glViewport(self.offset[0],
                      self.offset[1],
                      self.port_size,
                      self.port_size)

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height

        self.setViewPort()
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        gl.glOrtho(-1, 1, 1, -1, -1, 1)
