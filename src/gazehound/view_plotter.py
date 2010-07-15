# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# This module contains tools to convert pointpaths into images indicating
# where a subject's gaze lingered.

import numpy as np


class ScanpathPlotter(object):
    """Plots pointpath on a canvas"""

    def __init__(self, canvas, pointpath, draw_shape):
        super(ScanpathPlotter, self).__init__()
        self.canvas = canvas
        self.pointpath = pointpath
        self.draw_shape = draw_shape

    def draw_pointpath(self):
        scale_factor = 0.0
        for point in self.pointpath:
            scale_factor = 1
            self.canvas.add_matrix(self.view_matrix, (point.x, point.y))


class Canvas(object):

    def __init__(self, width, height, dtype=np.float, fill_value=0.0):
        super(Canvas, self).__init__()
        self.data = np.zeros((width, height), dtype=dtype)
        self.data += fill_value

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def width(self):
        return self.data.shape[1]

    def height(self):
        return self.data.shape[0]

    def add_matrix(self, source, target_point):
        # Correct for target_point indicating center
        px, py = (
            (target_point[0]-len(source)/2),
            (target_point[1]-len(source[0])/2))
        # Compute ranges for source and target...
        sx1 = min(max(0, -px), len(source))
        sy1 = min(max(0, -py), len(source[0]))
        sx2 = max(min(len(source), (self.width() - px)), 0)
        sy2 = max(min(len(source[0]), (self.height() - py)), 0)

        tx1 = min(max(0, px), self.width())
        ty1 = min(max(0, py), self.height())
        tx2 = max(min(self.width(), (len(source) + px)), 0)
        ty2 = max(min(self.height(), (len(source[0]) + py)), 0)

        xcount = min((sx2-sx1), (tx2-tx1))
        ycount = min((sy2-sy1), (ty2-ty1))

        for i in range(0, xcount):
            for j in range(0, ycount):
                self[tx1+i][ty1+j] += source[sx1+i][sy1+j]

    def clip_to(self, min_val=None, max_val=None):
        for i in range(0, self.width()):
            for j in range(0, self.height()):
                if min_val is not None:
                    self.data[i][j] = max(self.data[i][j], min_val)
                if max_val is not None:
                    self.data[i][j] = min(self.data[i][j], max_val)
