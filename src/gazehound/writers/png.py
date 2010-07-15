# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# Handles creating .png images from canvasses.

import array
import struct
from gazehound.ext import png


class CanvasWriter(object):

    def __init__(self, width, height, channels, bytes_per_sample = 1):
        """
        Create a new CanvasWriter

        height, width: dimensions of the image, in pixels

        channels: a list or tuple whose elements are either floating point
        numbers in (0,1) or Canvas objects with elements as floats in (0,1).
        Canvases must have 1, 3, or 4 elements -- for greyscale, truecolor,
        or truecolor + alpha images. Indexed color images are not supported.
        If the value is a float, this assumes that value will be used for
        the entire image.
        If the value is a Canvas, its height and width must equal the
        given height and width.
        Order of channels:
        if len = 1: grey
        if len = 3: red, green, blue
        if len = 4: red, green, blue, alpha

        Larger values of alpha => more opacity

        bytes_per_sample: 1 or 2, depending on whether each channel should
        be represented by 8 or 16 bits per pixel.

        """
        super(CanvasWriter, self).__init__()
        self.width = width
        self.height = height
        self.bytes_per_sample = bytes_per_sample

        self.channels = channels

    def to_bytes(self):
        MAX_VALS = {1: 255, 2: 65535}
        MAX = MAX_VALS[self.bytes_per_sample]

        byte_width = len(self.channels)*self.width*self.bytes_per_sample
        ar = []
        for i in range(0, self.height):
            vals = [0]*len(self.channels)*self.width
            for j in range(0, self.width):
                # Add each channel's data to a list of ints, scaled properly
                for k in range(0, len(self.channels)):
                    if hasattr(self.channels[k], '__getitem__'):
                        val = self.channels[k][j][i]
                    else:
                        val = self.channels[k]
                    val = int(val*MAX)
                    vals[(j*len(self.channels))+k] = val
            if self.bytes_per_sample > 1:
                # Pack and unpack the ints to get the proper ordering...
                fmt_str = ">"+str(self.width*len(self.channels))+"H"
                packed = struct.pack(fmt_str, *vals)
                bfs = str(byte_width)+"B"
                bytes = struct.unpack(bfs, packed)
                ar.append(array.array('B', bytes))

            else:
                ar.append(array.array('B', vals))

        return ar

    def has_alpha(self):
        return len(self.channels) == 4

    def greyscale(self):
        return len(self.channels) == 1

    def write(self, file, compression = None):
        w = png.Writer(
            width = self.width,
            height = self.height,
            has_alpha = self.has_alpha(),
            bytes_per_sample = self.bytes_per_sample,
            greyscale = self.greyscale(),
            compression = compression)
        w.write(file, self.to_bytes())
