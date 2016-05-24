# distutils: language = c++
# distutils: sources = filereader.cpp

import sys
import os

from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp.string cimport string
from libcpp cimport bool

import numpy as np

from PyQt4 import QtCore, QtGui

color_fname = "chochin_palette.py"
if os.path.isfile(color_fname):
    sys.path.append(".")
    import chochin_palette
    color_palette = np.array(chochin_palette.color_palette, dtype=np.object)
else:
    color_palette = np.array([QtCore.Qt.black,
                              QtCore.Qt.gray,
                              QtCore.Qt.white,
                              QtCore.Qt.green,
                              QtCore.Qt.yellow,
                              QtCore.Qt.red,
                              QtCore.Qt.blue,
                              QtCore.Qt.magenta,
                              QtCore.Qt.darkGreen,
                              QtCore.Qt.cyan,
                              QtCore.Qt.gray,
                              QtCore.Qt.white,
                              QtCore.Qt.green,
                              QtCore.Qt.yellow,
                              QtCore.Qt.red,
                              QtCore.Qt.blue,
                              QtCore.Qt.magenta,
                              QtCore.Qt.darkGreen,
                              QtCore.Qt.cyan],
                             dtype=np.object)

color_palette = np.array([QtGui.QColor(c).getRgbF() for c in color_palette])

cdef extern from "filereader.cpp":
    cdef cppclass filereader:
          filereader(string) except +
          map[string, vector[vector[float]]] positions
          map[string, vector[float]] thicknesses
          map[string, vector[int]] colors
          map[string, vector[int]] layers
          map[string, vector[string]] texts

          bool get()

cdef class chochinFile:
    cdef filereader *thisptr      # hold a C++ instance which we're wrapping
    frames = []

    def __cinit__(self, string fname):
        self.thisptr = new filereader(fname)

    def __dealloc__(self):
        del self.thisptr

    def size(self, obj_type):
        return self.thisptr.positions[obj_type.encode("utf8")].size()

    def get_pos(self, obj_type):
        obj_str = obj_type.encode("utf8")
        n = self.size(obj_type)
        if n == 0:
            return None
        return np.array(self.thisptr.positions[obj_str])

    def get_attrs(self, obj_type):
        obj_str = obj_type.encode("utf8")
        n = self.size(obj_type)
        if n == 0:
            return None

        if obj_type in ["c", "s"]:
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4),
                                 ('r', np.float32, 1)])
            attrs['y'] = self.thisptr.layers[obj_str]
            attrs['@'] = color_palette[self.thisptr.colors[obj_str]]
            attrs['r'] = self.thisptr.thicknesses[obj_str]

        if obj_type == "l":
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4)])
            attrs['y'] = self.thisptr.layers[obj_str]
            attrs['@'] = color_palette[self.thisptr.colors[obj_str]]

        if obj_type == "t":
            attrs = np.empty(n, [('y', np.uint8, 1),
                         ('@', np.float32, 4),
                         ('s', ('U', 100))])
            attrs['y'] = self.thisptr.layers[obj_str]
            attrs['@'] = color_palette[self.thisptr.colors[obj_str]]
            attrs['s'] = self.thisptr.texts[obj_str]

        return attrs

    def read_chunk(self):
        while self.thisptr.get():
            pos_d = {k: self.get_pos(k)
                     for k in ["c", "s", "l", "t"]
                     if self.size(k) > 0}
            attrs_d = {k: self.get_attrs(k)
                       for k in ["c", "s", "l", "t"]
                       if self.size(k) > 0}
            self.frames.append((pos_d, attrs_d))
