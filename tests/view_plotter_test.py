# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from nose.tools import eq_
from testutils import gt_, lt_, gte_, lte_, includes_
import mock_objects

import array

from gazehound import view_plotter, shapes

#class TestScanpathPlotter(object):
#    def __init__(self):
#        super(TestScanpathPlotter, self).__init__()
#
#    def setup(self):
#        # I'm gonna make a mini-canvas...
#        self.canvas = view_plotter.Canvas(
#            height = 600, width = 400, type_str = 'f', fill_value = 0.0
#        )
#        self.scanpath = mock_objects.smi_scanpath_spreadout()
#        self.view_matrix = shapes.Ellipse(0,0,20,20).to_matrix()
#        
#    def teardown(self):
#        pass
#        
#    def test_plotter_draws_on_matrix(self):
#        p = view_plotter.ScanpathPlotter(
#            canvas = self.canvas,
#            scanpath = self.scanpath,
#            view_matrix = self.view_matrix
#        )
#        p.draw_scanpath()
#        p1 = self.scanpath[0]
#        gt_(p.canvas[p1.x][p1.y], 0)
#        
#    
#class TestCanvas(object):
#    def __init__(self):
#        super(TestCanvas, self).__init__()
#    
#    def setup(self):
#        self.rect = shapes.Rectangle(0,0,2,2)
#        self.rmat = self.rect.to_matrix('f', 1.0)
#        self.canvas = view_plotter.Canvas(
#            width = 10, height = 8, 
#            type_str = 'f', fill_value = 0.0
#        )
#        
#    def teardown(self):
#        pass
#    
#    def test_canvas_has_height_and_width(self):
#        c = view_plotter.Canvas(
#            width = 10,
#            height = 8
#        )
#        eq_(c.width(), 10)
#        eq_(c.height(), 8)
#        
#    def test_canvas_is_indexable(self):
#        c = view_plotter.Canvas(
#            width = 10, height = 7, 
#            type_str = 'f', fill_value = 1.0
#        )
#        c[0][0]
#    
#    def test_canvas_sets_proper_type_and_value(self):
#        c = view_plotter.Canvas(
#            width = 10, height = 7, 
#            type_str = 'f', fill_value = 1.0
#        )
#        eq_(c[0][0], 1.0)
#        eq_(type(c[0][0]), type(1.0))
#        
#    def test_canvas_add_matrix_adds_from_origin(self):
#        self.canvas.add_matrix(self.rmat, (0,0))
#        eq_(self.canvas[0][0], 1.0)
#        eq_(self.canvas[1][1], 0.0)
#        
#        
#    def test_canvas_adds_matrix_adds_from_1_1(self):
#        self.canvas.add_matrix(self.rmat, (1,1))
#        eq_(self.canvas[0][0], 1.0)
#        eq_(self.canvas[1][1], 1.0)
#        
#    def test_canvas_adds_matrix_adds_from_oob_topleft(self):
#        self.canvas.add_matrix(self.rmat, (-2,-2))
#        eq_(self.canvas[0][0], 0.0)
#
#    def test_canvas_adds_matrix_adds_from_oob_bottomright(self):
#        self.canvas.add_matrix(self.rmat, (11,9))
#        eq_(self.canvas[9][7], 0.0)
#    
#    def test_canvas_clips_max(self):
#        self.canvas[0][0] = 2.0
#        self.canvas[0][1] = 0.7
#        self.canvas.clip_to(max_val = 1.0)
#        eq_(round(self.canvas[0][0]*10), 10.0)
#        eq_(round(self.canvas[0][1]*10), 7.0)
#    
#    def test_canvas_clips_min(self):
#        self.canvas[0][0] = -2.0
#        self.canvas[0][1] = 0.7
#        self.canvas.clip_to(min_val = 0.0)
#        eq_(round(self.canvas[0][0]*10), 0.0)
#        eq_(round(self.canvas[0][1]*10), 7.0)
#            