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
  cdef struct Frame:
    map[string, vector[float]] positions
    map[string, vector[float]] thicknesses
    map[string, vector[int]] colors
    map[string, vector[int]] layers
    map[string, vector[string]] texts

cdef extern from "filereader.cpp":
    cdef cppclass filereader:
          filereader(string) except +
          vector[Frame] frames
          bool get()

cdef class chochinFile:
    cdef filereader *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self, string fname):
        self.thisptr = new filereader(fname)

    def __dealloc__(self):
        del self.thisptr

    def read_chunk(self):
        while self.thisptr.get():
            pass

    def get_attrs(self, index):
        frame_data = self.thisptr.frames[index]
        attrs = {}
        for o in frame_data.positions.keys():
            o_str = o.decode()
            if o == b"c" or o == b"s":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', np.int, 1),
                                            ('@', np.float32, 4),
                                            ('r', np.float32, 1)])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = color_palette[frame_data.colors[o]]
                attrs[o_str]['r'] = frame_data.thicknesses[o]
            elif o == b"l":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', np.uint8, 1),
                                        ('@', np.float32, 4)])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = color_palette[frame_data.colors[o]]
            elif o == b"t":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', np.uint8, 1),
                                        ('@', np.float32, 4),
                                        ('s', ('U', 100))])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = color_palette[frame_data.colors[o]]
                attrs[o_str]['s'] = frame_data.texts[o]

        return attrs

    def __getitem__(self, index):
        frame_data = self.thisptr.frames[index]
        pos = {}
        size = {b'c': 3,
                b's': 6,
                b'l': 6,
                b't': 3}
        # print(frame_data.keys())
        for o in frame_data.positions.keys():
            o_str = o.decode()
            pos[o_str] = np.array(frame_data.positions[o],
                                  dtype=np.float32)
            pos[o_str].shape = (-1, size[o])
        attrs = self.get_attrs(index)

        return pos, attrs

    def frame_nb(self):
        return self.thisptr.frames.size()
