# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
import StringIO

from nose.tools import eq_
from ..testutils import gt_, lt_, includes_, print_matrix
from .. import mock_objects

from gazehound import view_plotter, shapes
from gazehound.writers import png

class TestPngWriter(object):
    def __init__(self):
        super(TestPngWriter, self).__init__()
        
    def setup(self):
        pass
    
    def teardown(self):
        pass
        
    
    def test_init_works(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.0],
        )
        
    def test_to_bytes_produces_array(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.0]
        )
        
        bytes = pw.to_bytes()
        eq_(len(bytes), pw.height)
        eq_(len(bytes[0]), len(pw.channels)*pw.width*pw.bytes_per_sample)
        
    def test_to_bytes_sets_width_with_multiple_channels(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.0, 0.0, 0.0]
        )
        bytes = pw.to_bytes()
        eq_(len(bytes[0]), len(pw.channels)*pw.width*pw.bytes_per_sample)
        
    def test_to_bytes_sets_width_with_bps_2(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.0, 0.0, 0.0],
            bytes_per_sample = 2
        )
        bytes = pw.to_bytes()
        eq_(len(bytes[0]), len(pw.channels)*pw.width*2)
        
    
    def test_to_bytes_sets_values_single_channel_single_value_1bpp(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75]
        )
        bytes = pw.to_bytes()
        eq_(bytes[0][0], int((0.75*255)))
        
    def test_to_bytes_sets_values_single_channel_matrix_value_1bpp(self):
        rect = shapes.Rectangle(0,0,10,8)
        mat = rect.to_matrix(fill_value = 0.75)
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [mat]
        )
        bytes = pw.to_bytes()
        eq_(bytes[0][0], int((0.75*255)))
        
    def test_to_bytes_sets_values_single_channel_single_value_2bpp(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75],
            bytes_per_sample = 2
        )
        bytes = pw.to_bytes()
        eq_(bytes[0][0], 191)
        eq_(bytes[0][1], 255)
    
    def test_has_alpha_works(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75])
        assert pw.has_alpha() == False

        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75, 0.75, 0, 0])
        assert pw.has_alpha() == True
    
    def test_greyscale_works(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75])
        assert pw.greyscale() == True

        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [0.75,1,1])
        assert pw.greyscale() == False
    
    def test_to_bytes_produces_uniform_matrix_from_single_values(self):
        pw = png.CanvasWriter(
            width = 10, height = 8,
            channels = [1, 0, 0])
        bytes = pw.to_bytes()
        vals = (255, 0, 0)
        for row in bytes:
            for i in range(0, len(row)):
                eq_(row[i], vals[i%3])
        
        
    def test_write_works(self):
        out = StringIO.StringIO()
        pw = png.CanvasWriter(
            width = 10, height = 8, 
            channels = [1, 0, 1, .5])
        eq_(out.getvalue(), '')
        pw.write(out)
        gt_(len(out.getvalue()), 0)
        out.close()