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

import sys
import os
import numpy as np
from PyQt4 import QtCore, QtGui
import numpy.core.defchararray as charray

color_fname = "chochin_palette.py"
if os.path.isfile(color_fname):
    sys.path.append(".")
    import chochin_palette
    color_palette = np.array(chochin_palette.color_palette, dtype=np.object)
else:
    color_palette = np.array([QtCore.Qt.black, QtCore.Qt.gray, QtCore.Qt.white,
                              QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.red,
                              QtCore.Qt.blue, QtCore.Qt.magenta,
                              QtCore.Qt.darkGreen, QtCore.Qt.cyan,
                              QtCore.Qt.gray, QtCore.Qt.white, QtCore.Qt.green,
                              QtCore.Qt.yellow, QtCore.Qt.red, QtCore.Qt.blue,
                              QtCore.Qt.magenta, QtCore.Qt.darkGreen,
                              QtCore.Qt.cyan], dtype=np.object)

color_palette = np.array([QtGui.QColor(c).getRgbF() for c in color_palette])


class chochinFileReader:
    def __init__(self, filename):

        self.is_file = True
        self.fname = filename
        self.chunksize = 10000000    # 10000000
        self.frames = []
        self.infile = open(self.fname, 'rb')
        self.trailing_frame = []
        self.trailing_attributes = []
        self.last_layer = 0
        self.last_color = color_palette[0]
        self.last_thickness = 0
        self.eof = False

    def get_layer_array(self):
        self.lswitch = self.cmd == 'y'
        layer_switches = np.empty(np.count_nonzero(self.lswitch)+2,
                                  dtype=np.int)
        layer_switches[0] = 0
        layer_switches[1:-1] = np.nonzero(self.lswitch)[0]
        layer_switches[-1] = self.cmd.shape[0]
        self.layers = np.empty(layer_switches.shape[0]-1, dtype=np.uint8)
        self.layers[0] = self.last_layer
        self.layers[1:] = np.genfromtxt(self.in_raw_data[layer_switches[1:-1]],
                                        usecols=1, dtype=np.uint8)
        self.layers = np.repeat(self.layers, np.diff(layer_switches))
        self.last_layer = self.layers[-1]

    def get_thickness_array(self):
        self.tswitch = self.cmd == 'r'
        thickness_switches =\
            np.empty(np.count_nonzero(self.tswitch)+2,
                     dtype=np.int)
        thickness_switches[0] = 0
        thickness_switches[1:-1] = np.nonzero(self.tswitch)[0]
        thickness_switches[-1] = self.cmd.shape[0]
        self.thicknesses = np.empty(thickness_switches.shape[0]-1,
                                    dtype=np.float32)
        self.thicknesses[0] = self.last_thickness
        self.thicknesses[1:] =\
            np.genfromtxt(self.in_raw_data[thickness_switches[1:-1]],
                          usecols=1, dtype=np.float32)
        self.thicknesses = np.repeat(self.thicknesses,
                                     np.diff(thickness_switches))
        self.last_thickness = self.thicknesses[-1]

    def get_color_array(self):
        self.cswitch = self.cmd == '@'
        color_switches = np.empty(np.count_nonzero(self.cswitch)+2,
                                  dtype=np.int)
        color_switches[0] = 0
        color_switches[1:-1] = np.nonzero(self.cswitch)[0]
        color_switches[-1] = self.cmd.shape[0]
        self.colors = np.empty((color_switches.shape[0]-1, 4),
                               dtype=np.float32)
        self.colors[0] = self.last_color
        self.colors[1:] =\
            color_palette[np.genfromtxt(self.in_raw_data[color_switches[1:-1]],
                                        usecols=1, dtype=np.int)]
        self.colors = np.repeat(self.colors, np.diff(color_switches), axis=0)

    def pruneSwitches(self):
        n = self.in_raw_data.shape[0]
        attribute_idx = np.zeros(n, dtype=np.bool)
        attribute_idx[self.cswitch] = True
        attribute_idx[self.lswitch] = True
        attribute_idx[self.tswitch] = True

        not_attribute_idx = np.logical_not(attribute_idx)
        self.in_raw_data = self.in_raw_data[not_attribute_idx]
        self.cmd = self.cmd[not_attribute_idx]
        self.layers = self.layers[not_attribute_idx]
        self.thicknesses = self.thicknesses[not_attribute_idx]
        self.colors = self.colors[not_attribute_idx]
        # correct the framebreak locations accordingly
        # by counting every attribute change between
        # every successive framebreaks
        self.framebreaks -=\
            np.cumsum(np.histogram(np.nonzero(attribute_idx)[0],
                                   np.append(0, self.framebreaks))[0])

    def read_chunk(self):

        if len(self.trailing_frame) > 0:
            self.in_raw_data =\
                np.append(self.trailing_frame,
                          np.array(self.infile.readlines()))
        else:
            self.in_raw_data = np.array(self.infile.readlines())
        # check eof
        if self.in_raw_data.shape[0] == 0:
            return False

        # ensure we have at least one frame
        # while not np.any(in_raw_data == b'\n'):
        #     b = np.array(self.infile.readlines(self.chunksize))
        #     if b.shape[0] == 0:
        #         break
        #     in_raw_data = np.vstack((in_raw_data, b))

        # framebreaks are lines with carriage return
        self.framebreaks = self.in_raw_data == b'\n'

        # remove the framebreaks lines in the raw data,
        # and keep a correct count of the break locations
        self.in_raw_data = self.in_raw_data[np.logical_not(self.framebreaks)]
        self.framebreaks = np.nonzero(self.framebreaks)[0]
        self.framebreaks -= np.arange(self.framebreaks.shape[0])

        # keep the bit after the last framebreak for next time,
        # as it is an incomplete frame
        self.trailing_frame = self.in_raw_data[self.framebreaks[-1]:]
        self.in_raw_data = self.in_raw_data[:self.framebreaks[-1]]
        self.framebreaks = self.framebreaks[:-1]

        # these are the commands, 'y', 'r', 'c', etc
        self.cmd = np.genfromtxt(self.in_raw_data, usecols=0, dtype=np.str)

        # now we want to propagate any attribute definition
        # like color, layer and thickness to the underneath commands,
        # up to the next attribute definition of the same kind

        # start with layer changes: we want to get an array 'layers',
        # with the same size as 'cmd', containing the layer
        # associated with every single line
        self.get_layer_array()

        # same for thicknesses
        self.get_thickness_array()

        # same for colors
        self.get_color_array()

        # now we will remove the attribute def lines from our arrays
        self.pruneSwitches()

        obj_pos = {}
        obj_attrs = {}

        o = "c"
        idx = np.nonzero(self.cmd == o)[0]
        n = idx.shape[0]
        if n > 0:
            obj_pos[o] = np.genfromtxt(self.in_raw_data[idx],
                                       usecols=[1, 2, 3],
                                       dtype=np.float32)
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4),
                                 ('r', np.float32, 1)])
            attrs['@'] = self.colors[idx]
            attrs['r'] = self.thicknesses[idx]
            attrs['y'] = self.layers[idx]
            breaks = np.digitize(self.framebreaks, idx)
            obj_pos[o] = np.split(obj_pos[o], breaks)
            obj_attrs[o] = np.split(attrs, breaks)

        o = "l"
        idx = np.nonzero(self.cmd == o)[0]
        n = idx.shape[0]
        if n > 0:
            obj_pos[o] = np.genfromtxt(self.in_raw_data[idx],
                                       usecols=np.arange(1, 7),
                                       dtype=np.float32)
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4)])
            attrs['@'] = self.colors[idx]
            attrs['y'] = self.layers[idx]
            breaks = np.digitize(self.framebreaks, idx)
            obj_pos[o] = np.split(obj_pos[o], breaks)
            obj_attrs[o] = np.split(attrs, breaks)

        o = "s"
        idx = np.nonzero(self.cmd == o)[0]
        n = idx.shape[0]
        if n > 0:
            obj_pos[o] = np.genfromtxt(self.in_raw_data[idx],
                                       usecols=np.arange(1, 7),
                                       dtype=np.float32)
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4),
                                 ('r', np.float32, 1)])
            attrs['@'] = self.colors[idx]
            attrs['r'] = self.thicknesses[idx]
            attrs['y'] = self.layers[idx]
            breaks = np.digitize(self.framebreaks, idx)
            obj_pos[o] = np.split(obj_pos[o], breaks)
            obj_attrs[o] = np.split(attrs, breaks)

        o = "t"
        idx = np.nonzero(self.cmd == o)[0]
        n = idx.shape[0]
        if n > 0:
            obj_pos[o] = np.genfromtxt(self.in_raw_data[idx],
                                       usecols=[1, 2, 3], dtype=np.float32)
            attrs = np.empty(n, [('y', np.uint8, 1),
                                 ('@', np.float32, 4),
                                 ('s', np.str, 1)])
            attrs['s'] =\
                np.array([t[-1].decode().strip("\n") for t in
                          charray.split(self.in_raw_data[idx], maxsplit=4)])
            attrs['@'] = self.colors[idx]
            attrs['y'] = self.layers[idx]
            breaks = np.digitize(self.framebreaks, idx)
            obj_pos[o] = np.split(obj_pos[o], breaks)
            obj_attrs[o] = np.split(attrs, breaks)

        for i in range(len(self.framebreaks)+1):
            pos_d = {k: obj_pos[k][i] for k in obj_pos}
            attrs_d = {k: obj_attrs[k][i] for k in obj_attrs}
            self.frames.append((pos_d, attrs_d))
        self.is_init = False
        return True
