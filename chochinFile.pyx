# distutils: language = c++
# distutils: sources = filereader.cpp

from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map as umap
from libcpp.string cimport string
from libcpp cimport bool

import numpy as np

from PyQt5 import QtCore, QtGui


cdef extern from "filereader.cpp":
  cdef struct Frame:
    umap[string, vector[float]] positions
    umap[string, vector[float]] thicknesses
    umap[string, vector[vector[float]]] colors
    umap[string, vector[int]] layers
    umap[string, vector[string]] texts

cdef extern from "filereader.cpp":
    cdef cppclass filereader:
          filereader(string) except +
          vector[Frame] frames
          bool get()
          void setPalette(vector[ vector [float] ])

cdef class chochinFile:
    cdef filereader *thisptr      # hold a C++ instance which we're wrapping
    cdef color_palette
    def __cinit__(self, string fname):
        self.thisptr = new filereader(fname)

    def __dealloc__(self):
        del self.thisptr

    def readChunk(self):
        while self.thisptr.get():
            pass

    def setPalette(self, palette):
        self.thisptr.setPalette(palette)

    def get_attrs(self, index):
        frame_data = self.thisptr.frames[index]
        frame_data_pos = dict(frame_data.positions)
        attrs = {}
        for o in frame_data_pos.keys():
            o_str = o.decode()
            if o == b"c" or o == b"s":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', int, 1),
                                            ('@', float, 4),
                                            ('r', float, 1)])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = frame_data.colors[o]
                attrs[o_str]['r'] = frame_data.thicknesses[o]
            elif o == b"l":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', np.uint8, 1),
                                        ('@', float, 4)])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = frame_data.colors[o]
            elif o == b"t":
                n = frame_data.layers[o].size()
                attrs[o_str] = np.empty(n, [('y', np.uint8, 1),
                                        ('@', float, 4),
                                        ('s', ('U', 100))])
                attrs[o_str]['y'] = frame_data.layers[o]
                attrs[o_str]['@'] = frame_data.colors[o]
                attrs[o_str]['s'] = frame_data.texts[o]

        return attrs

    def __getitem__(self, index):
        frame_data_pos = dict(self.thisptr.frames[index].positions)
        pos = {}
        size = {b'c': 3,
                b's': 6,
                b'l': 6,
                b't': 3}
        for o in frame_data_pos.keys():
            o_str = o.decode()
            pos[o_str] = np.array(frame_data_pos[o],
                                  dtype=float)
            pos[o_str].shape = (-1, size[o])
        attrs = self.get_attrs(index)

        return pos, attrs

    def frame_nb(self):
        return self.thisptr.frames.size()
