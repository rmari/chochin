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

import numpy as np


class chochinScene:

    def __init__(self, obj_vals, obj_attrs):
        self.obj_vals = obj_vals
        self.obj_attrs = obj_attrs
        self.rotated = False

    def getBoundaries(self):
        minima = None
        maxima = None

        for k in self.obj_vals:
            if k != 't':
                pos = self.obj_vals[k]
            else:
                pos = self.obj_vals[k][0]
            mink = np.min(np.reshape(pos, (-1, 3)),
                          axis=0)
            maxk = np.max(np.reshape(pos, (-1, 3)),
                          axis=0)
            if minima is None:
                minima = mink[:]
                maxima = maxk[:]
            else:
                minima = np.minimum(minima, mink)
                maxima = np.maximum(maxima, maxk)

        return np.column_stack((minima, maxima))

    def getLargestDimension(self):
        boundaries = self.getBoundaries()
        if boundaries[0, 0] is not None:
            return np.max(boundaries[:, 1] - boundaries[:, 0])
        else:
            return 0

    def filterLayers(self, layer_mask, object_layer_attr):
        #  filter out layers
        active_layers = np.nonzero(layer_mask)[0]
        n = object_layer_attr.shape[0]
        displayed_idx = np.zeros(n, dtype=np.bool)
        for d in active_layers:
            displayed_idx = np.logical_or(displayed_idx,
                                          object_layer_attr == d)
        return np.nonzero(displayed_idx)[0]

    def setRotation(self, rotation):
        self.rotation = rotation
        self.rotated = False

    def rotate(self, positions):
        dim = positions.shape[1]
        if dim == 3:
            rotated_pos = np.dot(positions, self.rotation)
        if dim == 6:
            rotated_pos = np.hstack((np.dot(positions[:, :3], self.rotation),
                                     np.dot(positions[:, 3:6], self.rotation)))
        self.rotated = True
        return np.array(rotated_pos)  # dot sometimes returns a matrix!!! grrr

    def getDisplayedScene(self):
        displayed_pos = {}
        displayed_attrs = {}
        for k in self.obj_vals:
            if k == "c":
                displayed_pos[k] = self.obj_vals[k]
                displayed_attrs[k] = self.obj_attrs[k]
            elif k == "t":
                displayed_pos[k] = self.rotate(self.obj_vals[k])
                displayed_attrs[k] = self.obj_attrs[k]
            else:
                displayed_pos[k] = self.rotate(self.obj_vals[k])
                displayed_attrs[k] = self.obj_attrs[k]

        return displayed_pos, displayed_attrs
